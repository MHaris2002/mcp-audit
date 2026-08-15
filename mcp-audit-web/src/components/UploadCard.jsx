import { useRef, useState } from "react";
import { SAMPLE_CLEAN, SAMPLE_RISKY } from "../lib/sampleConfigs";

export default function UploadCard({ onInspect }) {
  const [text, setText] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  function readFile(file) {
    const reader = new FileReader();
    reader.onload = () => setText(reader.result);
    reader.readAsText(file);
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) readFile(file);
  }

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) readFile(file);
  }

  function handleInspect() {
    setError("");
    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch (e) {
      setError("That doesn't look like valid JSON. Check for a missing comma or bracket, and try again.");
      return;
    }
    onInspect(parsed);
  }

  return (
    <div className="tag-card">
      <div
        className={`dropzone ${dragOver ? "drag-over" : ""}`}
        tabIndex={0}
        role="button"
        aria-label="Upload MCP config file"
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        onDragEnter={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={(e) => { e.preventDefault(); setDragOver(false); }}
        onDrop={handleDrop}
      >
        <span className="dz-icon">📋</span>
        <p className="primary">Drop your config file here</p>
        <p>or click to browse — .json files only</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json,application/json"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
      </div>

      <div className="or-divider">or paste it directly</div>

      <textarea
        id="paste-input"
        placeholder='{ "mcpServers": { ... } }'
        spellCheck={false}
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      {error && <div className="error-msg">{error}</div>}

      <div className="tool-actions">
        <div className="sample-links">
          Try:{" "}
          <button onClick={() => setText(JSON.stringify(SAMPLE_CLEAN, null, 2))}>a clean example</button>
          {" · "}
          <button onClick={() => setText(JSON.stringify(SAMPLE_RISKY, null, 2))}>a risky example</button>
        </div>
        <button
          className="inspect-btn"
          disabled={text.trim().length === 0}
          onClick={handleInspect}
        >
          Inspect config
        </button>
      </div>

      <p className="privacy-note">🔒 Nothing you paste or upload ever leaves your browser. No server, no network calls.</p>

      <style>{`
        .tag-card {
          background: var(--paper);
          color: var(--ink-text);
          border-radius: 14px;
          padding: 28px;
          position: relative;
          box-shadow: 0 20px 50px -20px rgba(0,0,0,0.6);
        }
        .tag-card::before {
          content: "";
          position: absolute;
          top: -9px; left: 32px;
          width: 18px; height: 18px;
          border-radius: 50%;
          background: var(--ink);
          box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
        }
        .dropzone {
          border: 2px dashed rgba(16,27,45,0.25);
          border-radius: 10px;
          padding: 28px 20px;
          text-align: center;
          cursor: pointer;
          transition: border-color 0.15s ease, background 0.15s ease;
        }
        .dropzone:hover, .dropzone.drag-over {
          border-color: var(--amber);
          background: rgba(232,169,60,0.08);
        }
        .dropzone:focus-visible { outline: 2px solid var(--amber); outline-offset: 2px; }
        .dz-icon { font-size: 1.6rem; margin-bottom: 8px; display: block; }
        .dropzone p { margin: 0; font-size: 0.92rem; color: #4a5468; }
        .dropzone p.primary { font-weight: 500; color: var(--ink-text); margin-bottom: 4px; }

        .or-divider {
          display: flex;
          align-items: center;
          gap: 12px;
          margin: 18px 0;
          color: #8a92a3;
          font-family: var(--font-mono);
          font-size: 0.72rem;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }
        .or-divider::before, .or-divider::after {
          content: "";
          flex: 1;
          height: 1px;
          background: rgba(16,27,45,0.14);
        }

        #paste-input {
          width: 100%;
          min-height: 110px;
          resize: vertical;
          font-family: var(--font-mono);
          font-size: 0.82rem;
          border: 1px solid rgba(16,27,45,0.18);
          border-radius: 8px;
          padding: 12px 14px;
          background: #fff;
          color: var(--ink-text);
        }
        #paste-input:focus { outline: 2px solid var(--amber); outline-offset: 2px; }

        .tool-actions {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-top: 16px;
          flex-wrap: wrap;
          gap: 12px;
        }
        .sample-links {
          font-family: var(--font-mono);
          font-size: 0.76rem;
          color: #5a6478;
        }
        .sample-links button {
          background: none;
          border: none;
          color: var(--ink-text);
          text-decoration: underline;
          text-decoration-color: rgba(16,27,45,0.35);
          cursor: pointer;
          font-family: var(--font-mono);
          font-size: 0.76rem;
          padding: 0;
        }
        .sample-links button:hover { color: var(--amber); text-decoration-color: var(--amber); }

        .inspect-btn {
          font-family: var(--font-display);
          font-weight: 600;
          font-size: 0.95rem;
          background: var(--ink);
          color: var(--paper);
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          cursor: pointer;
          transition: transform 0.1s ease, background 0.15s ease;
        }
        .inspect-btn:hover:not(:disabled) { background: #1c2c47; }
        .inspect-btn:active:not(:disabled) { transform: scale(0.98); }
        .inspect-btn:disabled { opacity: 0.4; cursor: not-allowed; }

        .privacy-note {
          font-family: var(--font-mono);
          font-size: 0.7rem;
          color: var(--slate);
          margin-top: 14px;
          text-align: center;
        }

        .error-msg {
          background: rgba(209,72,58,0.1);
          border: 1px solid rgba(209,72,58,0.4);
          color: #ffd9d3;
          border-radius: 8px;
          padding: 12px 16px;
          font-size: 0.88rem;
          margin-top: 16px;
          font-family: var(--font-mono);
        }

        @media (max-width: 520px) {
          .tag-card { padding: 20px; }
          .tool-actions { flex-direction: column; align-items: stretch; }
          .inspect-btn { width: 100%; }
        }
      `}</style>
    </div>
  );
}
