"""
mcp-audit CLI entrypoint.

Usage:
    python -m mcp_audit.cli                 scan known global config locations
    python -m mcp_audit.cli --project .     also scan project-scoped configs in the given dir
    python -m mcp_audit.cli --file path.json  scan one specific file directly
"""

import argparse
from pathlib import Path

from rich.console import Console

from mcp_audit.locations import ConfigLocation, discover_config_files
from mcp_audit.report import print_report
from mcp_audit.scanner import scan_config_file, scan_many


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-audit",
        description="Scan MCP server configs for risky permissions and patterns. No AI, no network calls.",
    )
    parser.add_argument(
        "--project", "-p",
        type=str,
        default=None,
        help="Also scan project-scoped MCP configs (.cursor/mcp.json, .mcp.json) in this directory.",
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Scan a single specific config file directly, ignoring auto-discovery.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    console = Console()

    if args.file:
        result = scan_config_file(Path(args.file), client=Path(args.file).name)
        print_report([result], console=console)
        return

    project_dir = Path(args.project) if args.project else None
    locations = discover_config_files(project_dir=project_dir)
    results = scan_many(locations)
    print_report(results, console=console)


if __name__ == "__main__":
    main()
