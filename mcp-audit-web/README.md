# mcp-audit — web

A static, client-side companion to the [mcp-audit CLI](../README.md). Same 8 detection rules, same results — reimplemented in JavaScript so anyone can paste in a config and get an instant, visual report with no install and no server.

## Project structure

```
index.html              — entry HTML (fonts, metadata)
src/
  main.jsx               — React entry point
  App.jsx                — top-level layout
  components/
    Header.jsx            — top bar with wordmark + GitHub link
    Hero.jsx               — headline + ties UploadCard/ResultsPanel together
    UploadCard.jsx         — drop zone, paste box, sample buttons, Inspect button
    ResultsPanel.jsx       — the seal stamp, summary, and findings list
    FindingCard.jsx        — one card per individual finding
    ChecksGrid.jsx         — the "what it checks for" card grid
    Footer.jsx
  lib/
    ruleEngine.js          — the 8 detection rules, ported from the Python backend
    sampleConfigs.js        — the "clean" and "risky" example configs
    ruleInfo.js              — descriptions used by ChecksGrid
  styles/
    global.css              — shared design tokens (colors, fonts)
```

Each component keeps its own styles in a `<style>` tag at the bottom of the file — no CSS build tooling needed, and each file is self-contained and easy to read top to bottom.

## Setup

Requires [Node.js](https://nodejs.org) (LTS).

```bash
npm install
npm run dev
```

This starts a local dev server (usually `http://localhost:5173`) with hot reload.

## Building for production

```bash
npm run build
```

Outputs static files to `dist/` — this is what actually gets deployed.

## Deploying to GitHub Pages

1. In `vite.config.js`, confirm `base` matches your repo name: `base: '/mcp-audit/'` if your repo is `mcp-audit`, deployed at `username.github.io/mcp-audit/`.
2. Run `npm run build`.
3. Push the contents of `dist/` to a `gh-pages` branch (or use a GitHub Action — see the project's main README for the CLI's own CI setup, which you can mirror for this).
4. In your repo's Settings → Pages, set the source to the `gh-pages` branch.

## A note on npm audit warnings

`npm audit` may report a moderate-severity issue in `esbuild`, a dependency of Vite's dev server. This only affects the local development server (it doesn't apply to the production build in `dist/`), so it's safe to leave as-is for a project at this stage.

## Keeping this in sync with the CLI

`ruleEngine.js` is a manual port of `mcp_audit/rules.py`. If you add or change a rule in the Python backend, mirror the same change here so the web version and the CLI never disagree. Both were verified to produce identical results against the same test fixtures (`tests/fixtures/*.json` in the main project).
