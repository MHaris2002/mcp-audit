import { SEVERITY_ORDER } from "../lib/ruleEngine";
import FindingCard from "./FindingCard";

export default function ResultsPanel({ findings, serverCount }) {
  const sorted = [...findings].sort((a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity]);
  const highCount = findings.filter((f) => f.severity === "high").length;
  const medCount = findings.filter((f) => f.severity === "medium").length;

  let sealClass = "clear";
  let sealLabel = "CLEAR";
  if (highCount > 0) {
    sealClass = "risk";
    sealLabel = "AT RISK";
  } else if (medCount > 0) {
    sealClass = "attention";
    sealLabel = "REVIEW";
  } else if (findings.length > 0) {
    sealClass = "attention";
    sealLabel = "MINOR NOTES";
  }

  const summaryText =
    findings.length === 0
      ? `No risky patterns found across ${serverCount} server${serverCount === 1 ? "" : "s"}.`
      : `${findings.length} finding${findings.length === 1 ? "" : "s"} across ${serverCount} server${serverCount === 1 ? "" : "s"}. Review each one manually.`;

  return (
    <div className="results-panel">
      <div className="seal-row">
        {/* key forces remount so the stamp animation replays on every new scan */}
        <div key={JSON.stringify(findings)} className={`seal ${sealClass}`}>{sealLabel}</div>
        <div className="seal-summary">
          <h2>{serverCount === 0 ? "No MCP servers found" : "Inspection complete"}</h2>
          <p>{summaryText}</p>
        </div>
      </div>

      <div className="perforation" />

      {findings.length === 0 ? (
        <div className="no-issues">✔ Nothing here looks risky.</div>
      ) : (
        sorted.map((f, i) => <FindingCard key={i} finding={f} />)
      )}

      <style>{`
        .results-panel { margin-top: 40px; }

        .seal-row {
          display: flex;
          align-items: center;
          gap: 20px;
          margin-bottom: 8px;
        }
        .seal {
          flex-shrink: 0;
          width: 84px; height: 84px;
          border-radius: 50%;
          border: 3px solid currentColor;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 0.72rem;
          letter-spacing: 0.02em;
          line-height: 1.2;
          transform: rotate(-6deg);
          animation: stamp 0.35s cubic-bezier(.2,1.4,.4,1);
        }
        @media (prefers-reduced-motion: reduce) {
          .seal { animation: none; }
        }
        @keyframes stamp {
          0% { transform: rotate(-6deg) scale(1.8); opacity: 0; }
          100% { transform: rotate(-6deg) scale(1); opacity: 1; }
        }
        .seal.clear { color: var(--teal); }
        .seal.attention { color: var(--amber); }
        .seal.risk { color: var(--crimson); }

        .seal-summary h2 {
          font-family: var(--font-display);
          font-size: 1.3rem;
          margin: 0 0 4px;
        }
        .seal-summary p {
          margin: 0;
          color: var(--slate);
          font-size: 0.92rem;
        }

        .perforation {
          height: 1px;
          background-image: repeating-linear-gradient(to right, var(--line) 0 6px, transparent 6px 12px);
          margin: 28px 0;
        }

        .no-issues {
          text-align: center;
          padding: 20px;
          color: var(--teal);
          font-family: var(--font-mono);
          font-size: 0.9rem;
        }

        @media (max-width: 520px) {
          .seal-row { align-items: flex-start; }
        }
      `}</style>
    </div>
  );
}
