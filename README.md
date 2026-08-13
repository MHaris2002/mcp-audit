# mcp-audit

**A static security scanner for MCP (Model Context Protocol) server configs — zero AI calls, zero network requests, zero GPU.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![No AI required](https://img.shields.io/badge/AI%20calls-none-brightgreen)](#why-this-exists)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg)](#contributing)

---

## Why this exists

MCP adoption has exploded across AI coding tools — Claude Desktop, Cursor, Claude Code, and others all let you plug in external "servers" that get real permissions: filesystem access, network calls, shell execution. Most developers install these with **zero visibility** into what they're actually granting.

This isn't hypothetical. In January 2026, critical vulnerabilities were discovered in Anthropic's own official Git MCP server — an officially maintained tool, not some random third-party package. If that can happen to an official server, unaudited third-party ones deserve real scrutiny.

`mcp-audit` scans the config files that control these permissions and flags patterns worth a human look — the same way a linter flags code smells rather than proving a bug exists.

## Table of contents

- [What it catches](#what-it-catches)
- [Supported clients](#supported-clients)
- [How it works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [CI / pre-commit usage](#ci--pre-commit-usage)
- [Example output](#example-output)
- [Project layout](#project-layout)
- [Adding a new rule](#adding-a-new-rule)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## What it catches

| Rule | Severity | What it flags |
|---|---|---|
| `hardcoded_secret` | 🔴 High | API keys, tokens, or passwords written as literal values instead of `${ENV_VAR}` references |
| `insecure_transport` | 🔴 High | Remote server URLs using unencrypted `http://` instead of `https://` |
| `dangerous_flag` | 🔴 High | Flags like `--dangerously-skip-permissions` that disable normal safety prompts |
| `broad_filesystem_access` | 🟠 Medium | Servers granted access to broad roots (`/`, `~`, `/home`) instead of a specific project folder |
| `shell_metacharacters` | 🟠 Medium | Arguments containing `;`, `&&`, `` ` ``, or `$(...)` — worth a manual check for command injection |
| `unpinned_version` | 🔵 Low | Packages installed with `@latest` instead of a pinned version, which can change behavior without warning |

Every finding includes a plain-English explanation. The tool **never makes a final verdict** — it surfaces patterns for a human to review.

## Supported clients

| Client | Global config | Project config |
|---|---|---|
| Claude Desktop | ✅ Standard install + Microsoft Store install | — |
| Cursor | ✅ `~/.cursor/mcp.json` | ✅ `.cursor/mcp.json` |
| Generic / custom | — | ✅ `.mcp.json` |

> Claude Code support is in progress — see [Roadmap](#roadmap).

## How it works

```mermaid
flowchart LR
    A["Config files\n(Claude Desktop, Cursor)"] --> B["locations.py\nfinds files per OS"]
    B --> C["scanner.py\nloads and parses JSON"]
    C --> D["rules.py\nstatic rule engine"]
    D --> E{Findings?}
    E -->|Yes| F["report.py\ncolored terminal report"]
    E -->|No| G["Clean"]
    D --> H["--json flag\nmachine-readable output"]
    F --> I["--fail-on flag\nexit code for CI"]
    H --> I
```

Everything runs locally, synchronously, with no network calls — the entire scan of a typical config completes in well under a second.

## Installation

```bash
git clone https://github.com/YOUR-USERNAME/mcp-audit.git
cd mcp-audit
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

| Command | What it does |
|---|---|
| `python -m mcp_audit.cli` | Scans known global config locations (Claude Desktop, Cursor) |
| `python -m mcp_audit.cli --project .` | Also scans project-scoped configs in the given directory |
| `python -m mcp_audit.cli --file path.json` | Scans one specific file directly |
| `python -m mcp_audit.cli --json` | Outputs machine-readable JSON instead of the colored report |
| `python -m mcp_audit.cli --fail-on <level>` | Sets the minimum severity that triggers a non-zero exit code |

### Try it on the included examples first

```bash
python3 -m mcp_audit.cli --file tests/fixtures/clean_config.json
python3 -m mcp_audit.cli --file tests/fixtures/risky_config.json
```

## CI / pre-commit usage

`--fail-on` controls when the command exits non-zero, which is how CI systems and pre-commit hooks detect failure:

```bash
python3 -m mcp_audit.cli --fail-on high    # default — fail only on high-severity findings
python3 -m mcp_audit.cli --fail-on medium  # fail on medium severity or above
python3 -m mcp_audit.cli --fail-on any     # fail on any finding at all
python3 -m mcp_audit.cli --fail-on none    # never fail — just report
```

Combine with `--json` to pipe structured results into another tool:

```bash
python3 -m mcp_audit.cli --json > scan-results.json
```

## Example output

Scanning the included risky test fixture:

```
mcp-audit  —  scanned 1 config file(s), 4 server(s) total

risky_config.json  tests/fixtures/risky_config.json
     Server                   Rule                     Details
 🔴  sketchy-remote           hardcoded_secret         header 'Authorization' contains what looks like a hardcoded credential.
 🔴  sketchy-remote           insecure_transport       server URL uses http:// instead of https:// — traffic is unencrypted.
 🔴  over-privileged-fs       hardcoded_secret         env var 'API_KEY' looks like a hardcoded credential.
 🔴  yolo-runner              dangerous_flag           flag '--dangerously-skip-permissions' disables a safety check.
 🟠  over-privileged-fs       broad_filesystem_access  argument '/' grants access to a broad filesystem root.
 🟠  shell-injection-looking  shell_metacharacters     argument contains shell metacharacters.
 🔵  over-privileged-fs       unpinned_version         'some-fs-server@latest' is unpinned.

7 finding(s) across all scanned files. Review each one manually.
```

## Project layout

```
mcp_audit/
  locations.py   — knows where each client stores its config file, per OS
  rules.py       — the static rule engine (add new rules here)
  scanner.py     — loads config files and runs rules against them
  report.py      — renders findings as a readable terminal report, or JSON
  cli.py         — the command-line entrypoint
tests/fixtures/  — example clean and risky configs used to verify the tool works
```

## Adding a new rule

Rules are plain functions in `rules.py`:

```python
def rule_my_new_check(server: str, config: dict) -> list[Finding]:
    ...
```

Add the function to `ALL_RULES` at the bottom of the file and it's automatically included in every scan. No other file needs to change.

## Roadmap

- [x] Static rule engine with 6 rules
- [x] Claude Desktop (incl. Microsoft Store install) + Cursor config discovery
- [x] JSON output mode for CI pipelines
- [x] Configurable exit codes via `--fail-on`
- [ ] Claude Code config support (`~/.claude.json`, nested project configs)
- [ ] Known-server allowlist + typosquat detection
- [ ] Community-maintained list of known-risky/known-good MCP servers
- [ ] `--fix` mode for safe, mechanical fixes (e.g. pinning versions)

## Contributing

Issues and PRs welcome — especially new rules, additional client support, or a larger known-server list. Rules are isolated, pure functions, so contributing a new one doesn't require touching the scanner or CLI.

## License

[MIT](LICENSE)
