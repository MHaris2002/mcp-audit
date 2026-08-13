"""
A small, curated list of well-known, official MCP server package
identifiers (npm packages, mainly). This is intentionally NOT
exhaustive --- it exists to catch two specific things:

1. Typosquatting: a package name that's suspiciously close to a real
   one (e.g. "@modelcontextprotocol/server-filesytem" missing a letter)
2. Giving a lower-confidence "unverified, not in our known list" nudge
   for anything that doesn't match a known package at all.

This list is meant to be community-extended over time via PRs, not
treated as a definitive security allowlist maintained by any authority.
"""

KNOWN_MCP_PACKAGES = {
    "@modelcontextprotocol/server-filesystem",
    "@modelcontextprotocol/server-github",
    "@modelcontextprotocol/server-memory",
    "@modelcontextprotocol/server-fetch",
    "@modelcontextprotocol/server-sequential-thinking",
    "@modelcontextprotocol/server-everything",
    "@modelcontextprotocol/server-puppeteer",
    "@modelcontextprotocol/server-brave-search",
    "@modelcontextprotocol/server-google-maps",
    "@modelcontextprotocol/server-postgres",
    "@modelcontextprotocol/server-sqlite",
    "@modelcontextprotocol/server-slack",
    "@notionhq/notion-mcp-server",
    "@sentry/mcp-server",
    "@upstash/context7-mcp",
    "@playwright/mcp",
}
