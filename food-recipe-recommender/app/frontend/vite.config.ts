import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Setup a server using Vite with a proxy to the backend Flask server.
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    }
  },
  // Vitest configuration for unit tests
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/setupTests.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      exclude: [
        'eslint.config.js',
        'vite.config.ts',
        'src/vite-env.d.ts',
        'src/js/main.tsx',
        'src/js/App.tsx',
        'src/js/pages/**',
      ],
    }
  }
})
