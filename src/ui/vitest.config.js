// vitest.config.js
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [
    // This is crucial to fix React version conflicts
    react()
  ],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['**/*.{test,spec}.{ts,tsx}'],
    // Add transformers to ensure React JSX is processed correctly
    transformMode: {
      web: [/\.[jt]sx$/]
    }
  },
  resolve: {
    alias: {
      // Add an alias for React to ensure only one version is used
      'react': path.resolve(__dirname, './node_modules/react'),
      'react-dom': path.resolve(__dirname, './node_modules/react-dom'),
      '@': path.resolve(__dirname, 'src'),
    },
  },
});
