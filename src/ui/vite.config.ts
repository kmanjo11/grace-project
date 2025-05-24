import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
// @ts-ignore - Ignore TypeScript errors for this config file
export default defineConfig({
  plugins: [react()],
  base: './', // Use relative paths to fix Docker container path issues
  root: '.', 
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
      },
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // Separate test config for Vitest
  define: {
    // This allows vitest to work without TypeScript errors
    'import.meta.vitest': 'undefined',
  },
});
