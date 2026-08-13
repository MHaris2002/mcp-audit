"""
Loads MCP config JSON files and runs the rule engine (rules.py)
against every server entry found inside them.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from mcp_audit.rules import Finding, run_all_rules


@dataclass
class ScanResult:
    config_path: Path
    client: str
    findings: list[Finding]
    server_count: int
    error: str | None = None


def load_config(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _find_mcp_server_blocks(data, _path="root") -> list[tuple[str, dict]]:
    """
    Recursively searches a parsed JSON structure for every dict found
    under an "mcpServers" key, at any depth. This handles both simple,
    flat configs (Claude Desktop, Cursor) and more deeply nested ones
    (Claude Code sometimes nests servers under a "projects" -> path
    structure). Returns a list of (context_label, servers_dict) pairs
    so findings can note which part of the file they came from.
    """
    blocks = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "mcpServers" and isinstance(value, dict):
                blocks.append((_path, value))
            elif isinstance(value, (dict, list)):
                blocks.extend(_find_mcp_server_blocks(value, _path=f"{_path}.{key}"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            blocks.extend(_find_mcp_server_blocks(item, _path=f"{_path}[{i}]"))
    return blocks


def scan_config_file(path: Path, client: str = "unknown") -> ScanResult:
    """
    Scans a single config file and returns a ScanResult. Malformed
    JSON or unreadable files are reported as a ScanResult with an
    error message rather than raising, so one bad file doesn't stop
    a multi-file scan.

    Searches the whole file recursively for any "mcpServers" blocks,
    rather than assuming one is present only at the top level ---
    some clients (notably Claude Code) can nest servers under a
    per-project structure.
    """
    try:
        config = load_config(path)
    except json.JSONDecodeError as e:
        return ScanResult(config_path=path, client=client, findings=[], server_count=0, error=f"invalid JSON: {e}")
    except OSError as e:
        return ScanResult(config_path=path, client=client, findings=[], server_count=0, error=f"could not read file: {e}")

    findings: list[Finding] = []
    server_count = 0

    for _context, servers in _find_mcp_server_blocks(config):
        for server_name, server_config in servers.items():
            if not isinstance(server_config, dict):
                continue
            server_count += 1
            findings.extend(run_all_rules(server_name, server_config))

    return ScanResult(
        config_path=path,
        client=client,
        findings=findings,
        server_count=server_count,
    )


def scan_many(locations) -> list[ScanResult]:
    """
    locations: iterable of objects with .path and .client attributes
    (see locations.ConfigLocation). Returns one ScanResult per file.
    """
    return [scan_config_file(loc.path, client=loc.client) for loc in locations]