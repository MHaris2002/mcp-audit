/**
 * Rule engine mirroring the Python backend (mcp_audit/rules.py and
 * mcp_audit/scanner.py) so the browser gives identical results to
 * the CLI. Pure functions only --- no DOM access here, so this file
 * can be unit tested independently of any UI.
 */

export const KNOWN_MCP_PACKAGES = [
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
];

const SECRET_LOOKING_KEYS = ["key", "token", "secret", "password", "credential", "auth"];
const BROAD_FS_PATHS = ["/", "~", "C:\\", "/home", "/Users", "/etc", "/root"];
const DANGEROUS_FLAGS = [
  "--dangerously-skip-permissions", "--yolo", "--allow-all", "--no-sandbox", "--trust-all",
];
const SHELL_METACHARACTERS = [";", "&&", "|", "$(", "`"];

export const SEVERITY_ORDER = { high: 0, medium: 1, low: 2, info: 3 };

function looksLikeLiteralSecret(value) {
  if (typeof value !== "string") return false;
  if (value.includes("${") || value.includes("$")) return false;
  if (["", "TODO", "CHANGEME", "YOUR_TOKEN_HERE", "YOUR_API_KEY"].includes(value.toUpperCase())) return false;
  return value.length >= 12;
}

export function levenshtein(a, b) {
  if (a === b) return 0;
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const curr = [i];
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      curr.push(Math.min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost));
    }
    prev = curr;
  }
  return prev[b.length];
}

function extractPackageNames(args) {
  const skip = new Set(["-y", "npx", "uvx", "node", "python", "python3"]);
  const names = [];
  for (const arg of args || []) {
    if (typeof arg !== "string") continue;
    if (arg.startsWith("-") || skip.has(arg)) continue;
    if (arg.startsWith(".") || arg.startsWith("/") || arg.startsWith("~") || /^[A-Za-z]:\\/.test(arg)) continue;
    const match = arg.match(/^(@[\w.-]+\/[\w.-]+|[\w.-]+)(@[\w.-]+)?$/);
    if (!match) continue;
    const base = match[1];
    if (base.length < 4) continue;
    names.push(base);
  }
  return names;
}

function finding(server, severity, rule, message) {
  return { server, severity, rule, message };
}

const RULES = [
  function hardcodedSecrets(server, config) {
    const out = [];
    const env = config.env || {};
    for (const [key, value] of Object.entries(env)) {
      if (SECRET_LOOKING_KEYS.some((w) => key.toLowerCase().includes(w)) && looksLikeLiteralSecret(value)) {
        out.push(finding(server, "high", "hardcoded_secret",
          `env var '${key}' looks like a hardcoded credential rather than a reference to an environment variable.`));
      }
    }
    const headers = config.headers || {};
    for (const [key, value] of Object.entries(headers)) {
      if (["authorization", "x-api-key"].includes(key.toLowerCase()) && looksLikeLiteralSecret(value)) {
        out.push(finding(server, "high", "hardcoded_secret",
          `header '${key}' contains what looks like a hardcoded credential.`));
      }
    }
    return out;
  },
  function insecureTransport(server, config) {
    if (typeof config.url === "string" && config.url.startsWith("http://")) {
      return [finding(server, "high", "insecure_transport",
        "server URL uses http:// instead of https:// — traffic (including any auth headers) is unencrypted.")];
    }
    return [];
  },
  function broadFilesystemAccess(server, config) {
    const out = [];
    for (const arg of config.args || []) {
      if (typeof arg === "string" && BROAD_FS_PATHS.includes(arg.trim())) {
        out.push(finding(server, "medium", "broad_filesystem_access",
          `argument '${arg}' grants access to a broad filesystem root rather than a specific project folder.`));
      }
    }
    return out;
  },
  function dangerousFlags(server, config) {
    const out = [];
    for (const arg of config.args || []) {
      if (DANGEROUS_FLAGS.includes(arg)) {
        out.push(finding(server, "high", "dangerous_flag",
          `flag '${arg}' disables a safety check — this server can act without normal permission prompts.`));
      }
    }
    return out;
  },
  function unpinnedVersion(server, config) {
    const out = [];
    for (const arg of config.args || []) {
      if (typeof arg === "string" && arg.endsWith("@latest")) {
        out.push(finding(server, "low", "unpinned_version",
          `'${arg}' is unpinned — a future release could change behavior or be compromised without you noticing.`));
      }
    }
    return out;
  },
  function shellMetacharacters(server, config) {
    const out = [];
    for (const arg of config.args || []) {
      if (typeof arg === "string" && SHELL_METACHARACTERS.some((ch) => arg.includes(ch))) {
        out.push(finding(server, "medium", "shell_metacharacters",
          `argument '${arg}' contains shell metacharacters, worth a manual look to confirm it's not command injection.`));
      }
    }
    return out;
  },
  function typosquatOrUnverified(server, config) {
    const out = [];
    for (const name of extractPackageNames(config.args)) {
      if (KNOWN_MCP_PACKAGES.includes(name)) continue;
      let closest = null;
      let closestDist = Infinity;
      for (const known of KNOWN_MCP_PACKAGES) {
        const d = levenshtein(name, known);
        if (d < closestDist) {
          closest = known;
          closestDist = d;
        }
      }
      if (closest && closestDist > 0 && closestDist <= 2) {
        out.push(finding(server, "high", "possible_typosquat",
          `package '${name}' is very close to the known official package '${closest}' (edit distance ${closestDist}) — double-check this isn't a typosquat.`));
      } else {
        out.push(finding(server, "info", "unverified_package",
          `package '${name}' is not in our known-server list. This doesn't mean it's unsafe, just unverified.`));
      }
    }
    return out;
  },
];

function runAllRules(server, config) {
  return RULES.flatMap((rule) => rule(server, config));
}

function findMcpServerBlocks(data) {
  const blocks = [];
  if (Array.isArray(data)) {
    for (const item of data) blocks.push(...findMcpServerBlocks(item));
  } else if (data && typeof data === "object") {
    for (const [key, value] of Object.entries(data)) {
      if (key === "mcpServers" && value && typeof value === "object") {
        blocks.push(value);
      } else if (value && typeof value === "object") {
        blocks.push(...findMcpServerBlocks(value));
      }
    }
  }
  return blocks;
}

/**
 * Scans a parsed MCP config object (already JSON.parse'd) and returns
 * { findings, serverCount }. This is the single entry point the UI
 * should call.
 */
export function scanConfig(parsed) {
  const findings = [];
  let serverCount = 0;
  for (const block of findMcpServerBlocks(parsed)) {
    for (const [serverName, serverConfig] of Object.entries(block)) {
      if (!serverConfig || typeof serverConfig !== "object") continue;
      serverCount++;
      findings.push(...runAllRules(serverName, serverConfig));
    }
  }
  return { findings, serverCount };
}
