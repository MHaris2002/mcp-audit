import { useState } from "react";
import UploadCard from "./UploadCard";
import ResultsPanel from "./ResultsPanel";
import { scanConfig } from "../lib/ruleEngine";

export default function Hero() {
  const [result, setResult] = useState(null);

  function handleInspect(parsedConfig) {
    setResult(scanConfig(parsedConfig));
  }

  return (
    <section className="hero">
      <div className="wrap">
        <h1>Know what your AI tools can actually do.</h1>
        <p className="sub">
          AI coding assistants like Claude Desktop, Claude Code, and Cursor connect to{" "}
          <strong>MCP servers</strong> — plugins that can read your files, make network calls, or run
          commands. Most people never see what permissions they've actually granted.
          Drop your config below to find out.
        </p>

        <UploadCard onInspect={handleInspect} />

        {result && <ResultsPanel findings={result.findings} serverCount={result.serverCount} />}
      </div>

      <style>{`
        .hero { padding: 56px 0 8px; }
        .hero h1 {
          font-family: var(--font-display);
          font-size: clamp(1.8rem, 4vw, 2.5rem);
          line-height: 1.15;
          margin: 0 0 14px;
          max-width: 15ch;
        }
        .hero p.sub {
          color: var(--slate);
          max-width: 52ch;
          margin: 0 0 32px;
          font-size: 1.02rem;
        }
        .hero p.sub strong { color: var(--paper); font-weight: 500; }
      `}</style>
    </section>
  );
}
