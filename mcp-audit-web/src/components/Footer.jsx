export default function Footer({ repoUrl }) {
  return (
    <footer className="site-footer">
      <div className="wrap">
        Static, client-side, source-available under MIT.{" "}
        <a href={repoUrl} target="_blank" rel="noopener noreferrer">View source &amp; CLI on GitHub</a>
      </div>

      <style>{`
        .site-footer {
          border-top: 1px solid var(--line);
          padding: 32px 0 48px;
          font-family: var(--font-mono);
          font-size: 0.76rem;
          color: var(--slate);
          text-align: center;
        }
        .site-footer a { color: var(--slate); text-decoration: underline; }
        .site-footer a:hover { color: var(--amber); }
      `}</style>
    </footer>
  );
}
