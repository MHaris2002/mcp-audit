import { RULE_INFO } from "../lib/ruleInfo";

const SEV_COLOR = { high: "var(--crimson)", medium: "var(--amber)", low: "var(--slate)", info: "#5c6577" };

export default function ChecksGrid() {
  return (
    <section className="checks-section">
      <div className="wrap">
        <h2>What it checks for</h2>
        <p>Eight patterns worth a human look — this tool never makes a final verdict, it just points you at what to review.</p>
        <div className="checks-grid">
          {RULE_INFO.map((c) => (
            <div className="check-item" key={c.name}>
              <h3>
                <span className="sev-dot" style={{ background: SEV_COLOR[c.sev] }} />
                {c.name}
              </h3>
              <p>{c.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .checks-section { padding: 64px 0; border-top: 1px solid var(--line); margin-top: 60px; }
        .checks-section h2 {
          font-family: var(--font-display);
          font-size: 1.4rem;
          margin-bottom: 8px;
        }
        .checks-section > .wrap > p {
          color: var(--slate);
          max-width: 56ch;
          margin-bottom: 32px;
        }
        .checks-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
          gap: 14px;
        }
        .check-item {
          border: 1px solid var(--line);
          border-radius: 10px;
          padding: 16px;
        }
        .check-item .sev-dot {
          display: inline-block;
          width: 8px; height: 8px;
          border-radius: 50%;
          margin-right: 8px;
        }
        .check-item h3 {
          font-family: var(--font-mono);
          font-size: 0.82rem;
          font-weight: 500;
          margin: 0 0 6px;
          display: flex;
          align-items: center;
        }
        .check-item p {
          font-size: 0.84rem;
          color: var(--slate);
          margin: 0;
        }
      `}</style>
    </section>
  );
}
