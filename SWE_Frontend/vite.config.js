import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/analysis': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ga': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/fitness': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/test': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/fault-localization': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/report': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})

