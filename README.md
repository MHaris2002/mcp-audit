# mcp-audit

A static security scanner for MCP (Model Context Protocol) server
configs — the config files that tell AI coding tools like Claude
Desktop, Claude Code, and Cursor which external tools they're allowed
to run and what access those tools have.

**No AI calls, no GPU, no network access required to run this.**
It's pure config parsing and pattern matching, like a linter.

## Why this exists

MCP adoption has exploded, but most developers install servers with
zero visibility into what permissions they're actually granting.
Anthropic's own official Git MCP server had critical vulnerabilities
discovered in it in January 2026. This tool surfaces the same kinds
of risky patterns automatically:

- Hardcoded secrets/tokens in config instead of environment variable references
- Servers using unencrypted `http://` instead of `https://`
- Overly broad filesystem access (e.g. granting access to `/` or `~`)
- Dangerous flags that disable permission prompts
- Unpinned package versions (`@latest`) that could change or be compromised without notice
- Shell metacharacters in arguments that could indicate command injection

It doesn't make a final verdict — it flags things worth a human look,
the same way a linter flags code smells rather than proving a bug exists.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Scan your machine's known MCP config locations (Claude Desktop, Cursor global config):

```bash
python3 -m mcp_audit.cli
```

Also scan project-scoped configs (`.cursor/mcp.json`, `.mcp.json`) in a specific folder:

```bash
python3 -m mcp_audit.cli --project /path/to/your/project
```

Scan one specific file directly:

```bash
python3 -m mcp_audit.cli --file path/to/config.json
```

## Try it on the included examples first

Before scanning your real configs, see it catch real issues on the
included test fixtures:

```bash
python3 -m mcp_audit.cli --file tests/fixtures/clean_config.json
python3 -m mcp_audit.cli --file tests/fixtures/risky_config.json
```

The clean fixture should report no issues. The risky fixture should
report 7 findings across all 5 rule types.

## Project layout

```
mcp_audit/
  locations.py   - knows where each client stores its config file, per OS
  rules.py       - the static rule engine (add new rules here)
  scanner.py     - loads config files and runs rules against them
  report.py      - renders findings as a readable terminal report
  cli.py         - the command-line entrypoint
tests/fixtures/  - example clean and risky configs used to verify the tool works
```

## Adding a new rule

Rules are plain functions in `rules.py` with the shape:

```python
def rule_my_new_check(server: str, config: dict) -> list[Finding]:
    ...
```

Add the function to `ALL_RULES` at the bottom of the file and it's
automatically included in every scan.

## Roadmap

- [x] Static rule engine with 5 initial rules
- [x] Claude Desktop + Cursor config discovery
- [ ] Claude Code config location support (once confirmed)
- [ ] Community-maintained list of known-risky/known-good MCP servers
- [ ] JSON output mode for CI pipelines
- [ ] `--fix` mode for safe, mechanical fixes (e.g. pinning versions)
