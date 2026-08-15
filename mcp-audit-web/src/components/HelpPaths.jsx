import { useState } from "react";

const PATHS = [
  {
    client: "Claude Desktop",
    entries: [
      { os: "Windows", path: "%APPDATA%\\Claude\\claude_desktop_config.json" },
      { os: "Windows (Microsoft Store install)", path: "%LOCALAPPDATA%\\Packages\\Claude_*\\LocalCache\\Roaming\\Claude\\claude_desktop_config.json" },
      { os: "macOS", path: "~/Library/Application Support/Claude/claude_desktop_config.json" },
    ],
  },
  {
    client: "Claude Code",
    entries: [
      { os: "Windows / macOS / Linux", path: "~/.claude.json" },
      { os: "Windows / macOS / Linux (alternate)", path: "~/.claude/settings.json" },
      { os: "Inside a specific project", path: ".claude/settings.json  (in the project folder)" },
    ],
  },
  {
    client: "Cursor",
    entries: [
      { os: "Windows / macOS / Linux", path: "~/.cursor/mcp.json" },
      { os: "Inside a specific project", path: ".cursor/mcp.json  (in the project folder)" },
    ],
  },
];

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard API can fail in some contexts (e.g. insecure origin) --- fail silently, the path is still visible to copy by hand.
    }
  }

  return (
    <button className="copy-btn" onClick={handleCopy} aria-label={`Copy path: ${text}`}>
      {copied ? "Copied ✓" : "Copy"}
    </button>
  );
}

export default function HelpPaths() {
  const [open, setOpen] = useState(false);

  return (
    <div className="help-paths">
      <button className="help-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        <span>{open ? "▾" : "▸"}</span> Where do I find my config file?
      </button>

      {open && (
        <div className="help-body">
          <p className="help-intro">
            Paste the path for your tool and OS into your file explorer's address bar and press Enter —
            on Windows, that's File Explorer; on Mac, open Finder and press <kbd>⌘</kbd>+<kbd>Shift</kbd>+<kbd>G</kbd> first.
          </p>

          {PATHS.map((group) => (
            <div className="help-group" key={group.client}>
              <h4>{group.client}</h4>
              {group.entries.map((entry) => (
                <div className="help-row" key={entry.path}>
                  <div className="help-os">{entry.os}</div>
                  <code className="help-path">{entry.path}</code>
                  <CopyButton text={entry.path} />
                </div>
              ))}
            </div>
          ))}

          <p className="help-note">
            Don't see a file at that path? That usually means you haven't added any MCP servers to that
            tool yet — there's nothing to scan, which is a perfectly good, safe state to be in.
          </p>
        </div>
      )}

      <style>{`
        .help-paths {
          margin-top: 18px;
        }
        .help-toggle {
          background: none;
          border: none;
          color: var(--slate);
          font-family: var(--font-mono);
          font-size: 0.8rem;
          cursor: pointer;
          padding: 4px 0;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .help-toggle:hover { color: var(--paper); }
        .help-toggle span { font-size: 0.7rem; }

        .help-body {
          background: rgba(239,234,224,0.05);
          border: 1px solid var(--line);
          border-radius: 10px;
          padding: 18px 20px;
          margin-top: 10px;
        }
        .help-intro {
          font-size: 0.86rem;
          color: var(--slate);
          margin: 0 0 18px;
        }
        .help-intro kbd {
          font-family: var(--font-mono);
          background: rgba(239,234,224,0.1);
          padding: 1px 6px;
          border-radius: 4px;
          font-size: 0.78rem;
        }
        .help-group { margin-bottom: 18px; }
        .help-group:last-of-type { margin-bottom: 0; }
        .help-group h4 {
          font-family: var(--font-display);
          font-size: 0.95rem;
          margin: 0 0 8px;
          color: var(--paper);
        }
        .help-row {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 6px 0;
          flex-wrap: wrap;
        }
        .help-os {
          font-size: 0.76rem;
          color: var(--slate);
          width: 100%;
          margin-bottom: 2px;
        }
        .help-path {
          font-family: var(--font-mono);
          font-size: 0.78rem;
          background: rgba(239,234,224,0.08);
          padding: 5px 10px;
          border-radius: 6px;
          flex: 1;
          min-width: 0;
          overflow-x: auto;
          white-space: nowrap;
          color: var(--paper);
        }
        .copy-btn {
          font-family: var(--font-mono);
          font-size: 0.72rem;
          background: none;
          border: 1px solid var(--line);
          color: var(--paper);
          padding: 4px 10px;
          border-radius: 6px;
          cursor: pointer;
          white-space: nowrap;
          flex-shrink: 0;
        }
        .copy-btn:hover { border-color: var(--amber); color: var(--amber); }

        .help-note {
          font-size: 0.8rem;
          color: var(--slate);
          margin: 16px 0 0;
          padding-top: 12px;
          border-top: 1px solid var(--line);
        }

        @media (max-width: 520px) {
          .help-path { white-space: normal; word-break: break-all; }
        }
      `}</style>
    </div>
  );
}
