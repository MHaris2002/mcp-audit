export default function Header({ repoUrl }) {
  return (
    <header className="site-header">
      <div className="wrap header-inner">
        <a href="#" className="wordmark">mcp<span>-audit</span></a>
        <nav>
          <a href={repoUrl} target="_blank" rel="noopener noreferrer">GitHub ↗</a>
        </nav>
      </div>

      <style>{`
        .site-header {
          padding: 28px 0 20px;
          border-bottom: 1px solid var(--line);
        }
        .header-inner {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .wordmark {
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 1.15rem;
          letter-spacing: -0.01em;
          color: var(--paper);
          text-decoration: none;
        }
        .wordmark span { color: var(--amber); }
        .site-header nav a {
          font-family: var(--font-mono);
          font-size: 0.8rem;
          color: var(--paper);
          text-decoration: none;
          border-bottom: 1px solid var(--line);
          padding-bottom: 2px;
        }
        .site-header nav a:hover { border-color: var(--amber); color: var(--amber); }
      `}</style>
    </header>
  );
}
