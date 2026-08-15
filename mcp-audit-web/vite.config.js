import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// If deploying to GitHub Pages at https://username.github.io/mcp-audit/,
// set base to '/mcp-audit/'. If deploying to a custom domain or the root
// of a site, change it to '/'.
export default defineConfig({
  plugins: [react()],
  base: '/mcp-audit/',
})
