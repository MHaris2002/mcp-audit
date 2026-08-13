"""
Static rules for inspecting a single MCP server entry from a config
file. No network calls, no AI, no external services --- pure pattern
matching against the parsed JSON structure.

Each rule is a plain function: (server_name, server_config) -> Finding | None
This makes it trivial to add new rules or let contributors add their
own without touching the scanner.
"""

import re
from dataclasses import dataclass

from mcp_audit.known_servers import KNOWN_MCP_PACKAGES

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}

# Heuristic keyword lists --- intentionally simple and inspectable,
# not an exhaustive security product. The goal is to surface things
# worth a human looking at, not to be a definitive verdict.
SECRET_LOOKING_KEYS = ("key", "token", "secret", "password", "credential", "auth")
BROAD_FS_PATHS = ("/", "~", "C:\\", "/home", "/Users", "/etc", "/root")
DANGEROUS_FLAGS = (
    "--dangerously-skip-permissions",
    "--yolo",
    "--allow-all",
    "--no-sandbox",
    "--trust-all",
)
SHELL_METACHARACTERS = (";", "&&", "|", "$(", "`")


@dataclass
class Finding:
    server: str
    severity: str   # high | medium | low | info
    rule: str
    message: str


def _looks_like_literal_secret(value: str) -> bool:
    """
    Heuristic: a literal, fairly long, non-placeholder-looking string.
    Values that reference environment variable expansion (e.g.
    "${SOME_VAR}" or "$SOME_VAR") are treated as safe references,
    not hardcoded secrets.
    """
    if not isinstance(value, str):
        return False
    # Env var references can appear standalone ("$TOKEN", "${TOKEN}")
    # or embedded after a prefix like "Bearer ${TOKEN}" --- treat any
    # of these as a safe reference, not a hardcoded literal.
    if "${" in value or "$" in value:
        return False
    if value.upper() in ("", "TODO", "CHANGEME", "YOUR_TOKEN_HERE", "YOUR_API_KEY"):
        return False
    return len(value) >= 12


def rule_hardcoded_secrets(server: str, config: dict) -> list[Finding]:
    findings = []
    env = config.get("env", {}) or {}
    for key, value in env.items():
        if any(word in key.lower() for word in SECRET_LOOKING_KEYS):
            if _looks_like_literal_secret(value):
                findings.append(Finding(
                    server=server,
                    severity="high",
                    rule="hardcoded_secret",
                    message=f"env var '{key}' looks like a hardcoded credential rather than a reference to an environment variable.",
                ))

    headers = config.get("headers", {}) or {}
    for key, value in headers.items():
        if key.lower() in ("authorization", "x-api-key") and _looks_like_literal_secret(value):
            findings.append(Finding(
                server=server,
                severity="high",
                rule="hardcoded_secret",
                message=f"header '{key}' contains what looks like a hardcoded credential.",
            ))
    return findings


def rule_insecure_transport(server: str, config: dict) -> list[Finding]:
    url = config.get("url", "")
    if isinstance(url, str) and url.startswith("http://"):
        return [Finding(
            server=server,
            severity="high",
            rule="insecure_transport",
            message="server URL uses http:// instead of https:// --- traffic (including any auth headers) is unencrypted.",
        )]
    return []


def rule_broad_filesystem_access(server: str, config: dict) -> list[Finding]:
    args = config.get("args", []) or []
    findings = []
    for arg in args:
        if isinstance(arg, str) and arg.strip() in BROAD_FS_PATHS:
            findings.append(Finding(
                server=server,
                severity="medium",
                rule="broad_filesystem_access",
                message=f"argument '{arg}' grants access to a broad filesystem root rather than a specific project folder.",
            ))
    return findings


def rule_dangerous_flags(server: str, config: dict) -> list[Finding]:
    args = config.get("args", []) or []
    findings = []
    for arg in args:
        if isinstance(arg, str) and arg in DANGEROUS_FLAGS:
            findings.append(Finding(
                server=server,
                severity="high",
                rule="dangerous_flag",
                message=f"flag '{arg}' disables a safety check --- this server can act without normal permission prompts.",
            ))
    return findings


def rule_unpinned_version(server: str, config: dict) -> list[Finding]:
    args = config.get("args", []) or []
    findings = []
    for arg in args:
        if isinstance(arg, str) and arg.endswith("@latest"):
            findings.append(Finding(
                server=server,
                severity="low",
                rule="unpinned_version",
                message=f"'{arg}' is unpinned --- a future release could change behavior or be compromised without you noticing. Consider pinning an exact version.",
            ))
    return findings


def rule_shell_metacharacters(server: str, config: dict) -> list[Finding]:
    args = config.get("args", []) or []
    findings = []
    for arg in args:
        if isinstance(arg, str) and any(ch in arg for ch in SHELL_METACHARACTERS):
            findings.append(Finding(
                server=server,
                severity="medium",
                rule="shell_metacharacters",
                message=f"argument '{arg}' contains shell metacharacters, worth a manual look to confirm it's not command injection.",
            ))
    return findings


def _levenshtein(a: str, b: str) -> int:
    """
    Standard edit-distance calculation, implemented directly so this
    project has zero extra dependencies beyond rich.
    """
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)

    previous_row = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        current_row = [i]
        for j, char_b in enumerate(b, start=1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (char_a != char_b)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


_PACKAGE_NAME_PATTERN = re.compile(r"^(@[\w.-]+/[\w.-]+|[\w.-]+)(@[\w.\-]+)?$")


def _extract_package_names(args: list) -> list[str]:
    """
    Pulls out anything in `args` that looks like an npm/pypi-style
    package identifier, stripping any @version suffix (including
    @latest). Skips flags (start with "-"), file paths (contain "/"
    without a leading "@" scope, or start with "." or a drive letter),
    and anything too short to be meaningful.
    """
    names = []
    for arg in args:
        if not isinstance(arg, str):
            continue
        if arg.startswith("-"):
            continue
        if arg in ("-y", "npx", "uvx", "node", "python", "python3"):
            continue
        # Looks like a filesystem path, not a package name --- skip.
        if arg.startswith((".", "/", "~")) or re.match(r"^[A-Za-z]:\\\\", arg):
            continue

        match = _PACKAGE_NAME_PATTERN.match(arg)
        if not match:
            continue
        base_name = match.group(1)
        if len(base_name) < 4:
            continue
        names.append(base_name)
    return names


def rule_unverified_or_typosquat_package(server: str, config: dict) -> list[Finding]:
    """
    For each package-looking argument:
    - exact match against KNOWN_MCP_PACKAGES -> no finding, it's known-good
    - very close (edit distance 1-2) to a known package but NOT exact ->
      high severity, likely typosquat
    - otherwise, if it looks like a real package identifier but isn't
      in our list at all -> info severity, "unverified, review manually"
    """
    args = config.get("args", []) or []
    findings = []

    for name in _extract_package_names(args):
        if name in KNOWN_MCP_PACKAGES:
            continue

        closest, closest_distance = None, None
        for known in KNOWN_MCP_PACKAGES:
            distance = _levenshtein(name, known)
            if closest_distance is None or distance < closest_distance:
                closest, closest_distance = known, distance

        if closest is not None and 0 < closest_distance <= 2:
            findings.append(Finding(
                server=server,
                severity="high",
                rule="possible_typosquat",
                message=f"package '{name}' is very close to the known official package '{closest}' "
                        f"(edit distance {closest_distance}) --- double-check this isn't a typosquat.",
            ))
        else:
            findings.append(Finding(
                server=server,
                severity="info",
                rule="unverified_package",
                message=f"package '{name}' is not in our known-server list. This doesn't mean it's "
                        f"unsafe, just that it hasn't been verified against a known-good registry --- worth a manual look.",
            ))

    return findings


ALL_RULES = [
    rule_hardcoded_secrets,
    rule_insecure_transport,
    rule_broad_filesystem_access,
    rule_dangerous_flags,
    rule_unpinned_version,
    rule_shell_metacharacters,
    rule_unverified_or_typosquat_package,
]


def run_all_rules(server: str, config: dict) -> list[Finding]:
    findings = []
    for rule in ALL_RULES:
        findings.extend(rule(server, config))
    return findings