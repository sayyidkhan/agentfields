import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // By default Vite only exposes env vars prefixed with VITE_ to the browser.
  // This app historically used OPENAI_API_KEY in `frontend/.env.local`, so we
  // also allow OPENAI_ for backwards compatibility.
  envPrefix: ['VITE_', 'OPENAI_'],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
