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


def scan_config_file(path: Path, client: str = "unknown") -> ScanResult:
    """
    Scans a single config file and returns a ScanResult. Malformed
    JSON or unreadable files are reported as a ScanResult with an
    error message rather than raising, so one bad file doesn't stop
    a multi-file scan.
    """
    try:
        config = load_config(path)
    except json.JSONDecodeError as e:
        return ScanResult(config_path=path, client=client, findings=[], server_count=0, error=f"invalid JSON: {e}")
    except OSError as e:
        return ScanResult(config_path=path, client=client, findings=[], server_count=0, error=f"could not read file: {e}")

    servers = config.get("mcpServers", {}) or {}
    findings: list[Finding] = []
    for server_name, server_config in servers.items():
        if not isinstance(server_config, dict):
            continue
        findings.extend(run_all_rules(server_name, server_config))

    return ScanResult(
        config_path=path,
        client=client,
        findings=findings,
        server_count=len(servers),
    )


def scan_many(locations) -> list[ScanResult]:
    """
    locations: iterable of objects with .path and .client attributes
    (see locations.ConfigLocation). Returns one ScanResult per file.
    """
    return [scan_config_file(loc.path, client=loc.client) for loc in locations]
