import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://inventario:8000',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api/, ''),
      },
      '/audit-api': {
        target: 'http://audit:8000',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/audit-api/, ''),
      },
    }
  }
})
