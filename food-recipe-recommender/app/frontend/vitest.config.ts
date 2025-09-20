import { defineConfig } from 'vitest/config'

export default defineConfig({
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
        'vitest.config.ts',
        'src/vite-env.d.ts',
        'src/js/main.tsx',
        'src/js/App.tsx',
        'src/js/pages/**',
      ],
    }
  }
})

