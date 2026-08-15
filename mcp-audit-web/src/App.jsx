import Header from "./components/Header";
import Hero from "./components/Hero";
import ChecksGrid from "./components/ChecksGrid";
import Footer from "./components/Footer";

const REPO_URL = "https://github.com/MHaris2002/mcp-audit";

export default function App() {
  return (
    <>
      <Header repoUrl={REPO_URL} />
      <main>
        <Hero />
        <ChecksGrid />
      </main>
      <Footer repoUrl={REPO_URL} />
    </>
  );
}
