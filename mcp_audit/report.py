"""
Renders ScanResult objects as a readable, colour-coded terminal
report using rich. No AI, no network --- just formatting.
"""

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
