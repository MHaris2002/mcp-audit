"""
Knows where each MCP-compatible client stores its config file, across
operating systems. Based on the emergent mcpServers JSON standard used
by Claude Desktop, Claude Code, and Cursor.

This module only computes PATHS. It does not read or modify anything.
"""

import os
import platform
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConfigLocation:
    client: str          # human-readable client name
    path: Path           # where the config file would live
    scope: str           # "global" or "project"


def _home() -> Path:
    return Path.home()


def known_global_locations() -> list[ConfigLocation]:
    """
    Returns the list of well-known global config file locations for
    supported clients, based on the current OS. Paths are returned
    whether or not the file actually exists --- the caller checks
    existence before reading.
    """
    system = platform.system()
    home = _home()
    locations = []

    # --- Claude Desktop ---
    if system == "Darwin":
        locations.append(ConfigLocation(
            client="Claude Desktop",
            path=home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
            scope="global",
        ))
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", str(home / "AppData" / "Roaming"))
        locations.append(ConfigLocation(
            client="Claude Desktop",
            path=Path(appdata) / "Claude" / "claude_desktop_config.json",
            scope="global",
        ))

        # Microsoft Store installs are sandboxed under a per-install
        # "Claude_<random suffix>" package folder rather than the
        # traditional AppData\Roaming\Claude path used by the direct
        # .exe installer. The suffix varies per machine, so we glob
        # for it instead of hardcoding a path.
        localappdata = os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local"))
        packages_dir = Path(localappdata) / "Packages"
        if packages_dir.exists():
            for package_dir in packages_dir.glob("Claude_*"):
                candidate = package_dir / "LocalCache" / "Roaming" / "Claude" / "claude_desktop_config.json"
                locations.append(ConfigLocation(
                    client="Claude Desktop (Microsoft Store)",
                    path=candidate,
                    scope="global",
                ))
    else:  # Linux (unofficial but common install path)
        locations.append(ConfigLocation(
            client="Claude Desktop",
            path=home / ".config" / "Claude" / "claude_desktop_config.json",
            scope="global",
        ))

    # --- Cursor (global) ---
    locations.append(ConfigLocation(
        client="Cursor",
        path=home / ".cursor" / "mcp.json",
        scope="global",
    ))

    return locations


def project_locations(project_dir: Path) -> list[ConfigLocation]:
    """
    Returns project-scoped config locations relative to a given
    project directory (e.g. the current working directory).
    """
    return [
        ConfigLocation(
            client="Cursor (project)",
            path=project_dir / ".cursor" / "mcp.json",
            scope="project",
        ),
        ConfigLocation(
            client="Generic MCP config (project)",
            path=project_dir / ".mcp.json",
            scope="project",
        ),
    ]


def discover_config_files(project_dir: Path | None = None) -> list[ConfigLocation]:
    """
    Returns every known config location that actually exists on disk,
    combining global (OS-level) locations with project-scoped ones if
    a project_dir is given.
    """
    candidates = known_global_locations()
    if project_dir is not None:
        candidates += project_locations(Path(project_dir))
    return [loc for loc in candidates if loc.path.exists()]
