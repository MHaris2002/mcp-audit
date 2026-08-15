export default function FindingCard({ finding }) {
  return (
    <div className={`finding-card ${finding.severity}`}>
      <div className="finding-head">
        <span className="finding-server">{finding.server}</span>
        <span className={`severity-chip ${finding.severity}`}>{finding.severity}</span>
      </div>
      <p className="finding-msg">{finding.message}</p>

      <style>{`
        .finding-card {
          background: var(--paper);
          color: var(--ink-text);
          border-radius: 10px;
          padding: 16px 18px;
          margin-bottom: 12px;
          border-left: 5px solid var(--slate);
        }
        .finding-card.high { border-left-color: var(--crimson); }
        .finding-card.medium { border-left-color: var(--amber); }
        .finding-card.low { border-left-color: var(--slate); }
        .finding-card.info { border-left-color: #b9c0cc; }

        .finding-head {
          display: flex;
          align-items: baseline;
          justify-content: space-between;
          gap: 12px;
          margin-bottom: 6px;
          flex-wrap: wrap;
        }
        .finding-server {
          font-family: var(--font-mono);
          font-weight: 500;
          font-size: 0.85rem;
        }
        .severity-chip {
          font-family: var(--font-mono);
          font-size: 0.68rem;
          letter-spacing: 0.04em;
          text-transform: uppercase;
          padding: 2px 8px;
          border-radius: 999px;
          white-space: nowrap;
        }
        .severity-chip.high { background: rgba(209,72,58,0.15); color: #a8281b; }
        .severity-chip.medium { background: rgba(232,169,60,0.2); color: #8a5f0e; }
        .severity-chip.low { background: rgba(124,135,152,0.18); color: #4a5468; }
        .severity-chip.info { background: rgba(124,135,152,0.12); color: #6b7383; }

        .finding-msg { font-size: 0.9rem; margin: 0; }
      `}</style>
    </div>
  );
}
