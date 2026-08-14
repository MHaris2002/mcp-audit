"""
Renders ScanResult objects as a readable, colour-coded terminal
report using rich, or as machine-readable JSON/SARIF. No AI, no
network --- just formatting.
"""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from mcp_audit.rules import SEVERITY_ORDER
from mcp_audit.scanner import ScanResult

SEVERITY_STYLE = {
    "high": "bold red",
    "medium": "yellow",
    "low": "cyan",
    "info": "dim",
}

SEVERITY_ICON = {
    "high": "🔴",
    "medium": "🟠",
    "low": "🔵",
    "info": "⚪",
}


def print_report(results: list[ScanResult], console: Console | None = None):
    console = console or Console()

    total_servers = sum(r.server_count for r in results)
    total_findings = sum(len(r.findings) for r in results)
    files_scanned = len(results)

    console.print()
    console.print(f"[bold]mcp-audit[/]  —  scanned [bold]{files_scanned}[/] config file(s), "
                   f"[bold]{total_servers}[/] server(s) total")
    console.print()

    if files_scanned == 0:
        console.print("[dim]No MCP config files found on this machine (checked known Claude Desktop and Cursor locations).[/]")
        return

    any_findings = False

    for result in results:
        console.print(f"[bold underline]{result.client}[/]  [dim]{result.config_path}[/]")

        if result.error:
            console.print(f"  [red]⚠ could not scan: {result.error}[/]")
            console.print()
            continue

        if not result.findings:
            console.print(f"  [green]✔ no issues found across {result.server_count} server(s)[/]")
            console.print()
            continue

        any_findings = True
        sorted_findings = sorted(result.findings, key=lambda f: SEVERITY_ORDER[f.severity])

        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
        table.add_column("", width=2)
        table.add_column("Server", style="bold")
        table.add_column("Rule")
        table.add_column("Details")

        for f in sorted_findings:
            table.add_row(
                SEVERITY_ICON[f.severity],
                f.server,
                f"[{SEVERITY_STYLE[f.severity]}]{f.rule}[/]",
                f.message,
            )
        console.print(table)
        console.print()

    if any_findings:
        console.print(f"[bold]{total_findings} finding(s) across all scanned files.[/] "
                       f"Review each one manually --- this tool flags patterns worth a "
                       f"human look, it does not make a final verdict.")
    else:
        console.print("[bold green]No risky patterns found in any scanned config.[/]")


def results_to_dict(results: list[ScanResult]) -> dict:
    """
    Converts scan results into a plain JSON-serializable dict, for use
    in CI pipelines, pre-commit hooks, or any other script that wants
    structured output instead of the human-readable report.
    """
    return {
        "files_scanned": len(results),
        "servers_scanned": sum(r.server_count for r in results),
        "total_findings": sum(len(r.findings) for r in results),
        "results": [
            {
                "client": r.client,
                "config_path": str(r.config_path),
                "server_count": r.server_count,
                "error": r.error,
                "findings": [
                    {
                        "server": f.server,
                        "severity": f.severity,
                        "rule": f.rule,
                        "message": f.message,
                    }
                    for f in r.findings
                ],
            }
            for r in results
        ],
    }


# --- SARIF (Static Analysis Results Interchange Format) support ---
#
# SARIF is the standard format GitHub's "Code Scanning" tab, GitLab,
# and most security dashboards consume natively. Uploading a SARIF
# file from a GitHub Actions workflow makes findings show up as
# inline annotations on the actual file, the same way CodeQL or
# other native security scanners do.

SARIF_LEVEL = {"high": "error", "medium": "warning", "low": "note", "info": "note"}

RULE_DESCRIPTIONS = {
    "hardcoded_secret": "A credential is written as a literal value instead of an environment variable reference.",
    "insecure_transport": "A server URL uses unencrypted http:// instead of https://.",
    "dangerous_flag": "A flag disables a normal safety or permission prompt.",
    "possible_typosquat": "A package name is suspiciously close to a known official package name.",
    "broad_filesystem_access": "A server is granted access to a broad filesystem root instead of a specific folder.",
    "shell_metacharacters": "An argument contains shell metacharacters that may indicate command injection.",
    "unpinned_version": "A package is installed without a pinned version.",
    "unverified_package": "A package is not present in the known-server registry.",
}


def _find_line_number(path: Path, server_name: str) -> int:
    """
    Best-effort lookup of the line where a server's JSON key appears
    in the raw file, so SARIF annotations point at roughly the right
    spot instead of always defaulting to line 1. Falls back to line 1
    if the file can't be read or the key can't be found --- this is a
    convenience for navigation, not a guarantee of exact placement.
    """
    try:
        text = path.read_text()
    except OSError:
        return 1
    needle = f'"{server_name}"'
    for i, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return i
    return 1


def _sarif_uri(path: Path) -> str:
    """
    SARIF wants forward-slash relative paths where possible (that's
    what GitHub Code Scanning expects to match against repo files).
    Falls back to the absolute path, slash-normalized, if the file
    isn't inside the current working directory.
    """
    try:
        rel = path.relative_to(Path.cwd())
    except ValueError:
        rel = path
    return str(rel).replace("\\", "/")


def results_to_sarif(results: list[ScanResult], repo_url: str = "") -> dict:
    """
    Converts scan results into a SARIF 2.1.0 document. Pass repo_url
    (e.g. "https://github.com/you/mcp-audit") to have it included as
    the tool's informationUri --- optional, but nice for provenance.
    """
    seen_rule_ids = set()
    sarif_rules = []
    sarif_results = []

    for result in results:
        for f in result.findings:
            if f.rule not in seen_rule_ids:
                seen_rule_ids.add(f.rule)
                sarif_rules.append({
                    "id": f.rule,
                    "shortDescription": {"text": RULE_DESCRIPTIONS.get(f.rule, f.rule)},
                    "defaultConfiguration": {"level": SARIF_LEVEL.get(f.severity, "warning")},
                })

            line = _find_line_number(result.config_path, f.server)
            sarif_results.append({
                "ruleId": f.rule,
                "level": SARIF_LEVEL.get(f.severity, "warning"),
                "message": {"text": f"[{f.server}] {f.message}"},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": _sarif_uri(result.config_path)},
                        "region": {"startLine": line},
                    }
                }],
            })

    driver = {
        "name": "mcp-audit",
        "version": "0.1.0",
        "rules": sarif_rules,
    }
    if repo_url:
        driver["informationUri"] = repo_url

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": driver},
            "results": sarif_results,
        }],
    }