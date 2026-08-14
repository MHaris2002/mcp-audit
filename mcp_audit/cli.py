"""
mcp-audit CLI entrypoint.

Usage:
    python -m mcp_audit.cli                 scan known global config locations
    python -m mcp_audit.cli --project .     also scan project-scoped configs in the given dir
    python -m mcp_audit.cli --file path.json  scan one specific file directly
    python -m mcp_audit.cli --json           machine-readable JSON output, for scripts/CI
    python -m mcp_audit.cli --sarif          SARIF output, for GitHub Code Scanning
    python -m mcp_audit.cli --fail-on medium exit non-zero if a medium+ severity finding exists
"""

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console

from mcp_audit.locations import discover_config_files
from mcp_audit.report import print_report, results_to_dict, results_to_sarif
from mcp_audit.rules import SEVERITY_ORDER
from mcp_audit.scanner import scan_config_file, scan_many

FAIL_ON_CHOICES = ["high", "medium", "low", "any", "none"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-audit",
        description="Scan MCP server configs for risky permissions and patterns. No AI, no network calls.",
    )
    parser.add_argument(
        "--project", "-p",
        type=str,
        default=None,
        help="Also scan project-scoped MCP configs (.cursor/mcp.json, .mcp.json, .claude/settings.json) in this directory.",
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Scan a single specific config file directly, ignoring auto-discovery.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of the human-readable report.",
    )
    parser.add_argument(
        "--sarif",
        action="store_true",
        help="Output SARIF 2.1.0 instead of the human-readable report, for GitHub Code Scanning and similar tools.",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Write output to this file instead of stdout (most useful with --json or --sarif).",
    )
    parser.add_argument(
        "--repo-url",
        type=str,
        default="",
        help="Optional repo URL included in SARIF output as tool provenance.",
    )
    parser.add_argument(
        "--fail-on",
        choices=FAIL_ON_CHOICES,
        default="high",
        help="Minimum severity that causes a non-zero exit code (for CI/pre-commit). "
             "'any' fails on any finding, 'none' always exits 0. Default: high.",
    )
    return parser


def _exit_code_for(results, fail_on: str) -> int:
    if fail_on == "none":
        return 0
    all_findings = [f for r in results for f in r.findings]
    if fail_on == "any":
        return 1 if all_findings else 0
    threshold = SEVERITY_ORDER[fail_on]
    return 1 if any(SEVERITY_ORDER[f.severity] <= threshold for f in all_findings) else 0


def main():
    parser = build_parser()
    args = parser.parse_args()
    console = Console()

    if args.file:
        results = [scan_config_file(Path(args.file), client=Path(args.file).name)]
    else:
        project_dir = Path(args.project) if args.project else None
        locations = discover_config_files(project_dir=project_dir)
        results = scan_many(locations)

    if args.sarif:
        output_text = json.dumps(results_to_sarif(results, repo_url=args.repo_url), indent=2)
    elif args.json:
        output_text = json.dumps(results_to_dict(results), indent=2)
    else:
        output_text = None  # print_report writes directly to console below

    if output_text is not None:
        if args.output:
            Path(args.output).write_text(output_text)
            console.print(f"[green]Wrote output to {args.output}[/]")
        else:
            print(output_text)
    else:
        print_report(results, console=console)

    sys.exit(_exit_code_for(results, args.fail_on))


if __name__ == "__main__":
    main()