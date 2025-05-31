import { defineConfig, loadEnv, type PluginOption } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
// @ts-ignore - Type definitions might be missing
import { visualizer } from 'rollup-plugin-visualizer';
// @ts-ignore - Type definitions might be missing
import { VitePWA } from 'vite-plugin-pwa';

// https://vitejs.dev/config/
export default defineConfig(({ mode, command: _command }) => {
  // Load env file based on `mode` in the current directory.
  const env = loadEnv(mode, process.cwd(), '');
  
  const isProduction = mode === 'production';
  const isDocker = env.DOCKER === 'true';

  return {
    plugins: [
      react({
        // Use React 17+ automatic JSX transform
        jsxImportSource: '@emotion/react',
        babel: {
          plugins: ['@emotion/babel-plugin'],
        },
      }) as PluginOption,
      // Visualize bundle size
      isProduction && visualizer({
        open: false,
        gzipSize: true,
        brotliSize: true,
      }),
      // PWA support
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
        manifest: {
          name: 'Grace Trading Platform',
          short_name: 'Grace',
          description: 'Advanced trading platform with Mango V3 integration',
          theme_color: '#1976d2',
          icons: [
            {
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png',
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png',
            },
          ],
        },
      }),
    ].filter(Boolean),

    // Base public path when served in production
    base: isProduction ? '/' : '/',
    
    // Root directory
    root: '.',

    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: !isProduction,
      minify: isProduction ? 'esbuild' : false,
      cssCodeSplit: true,
      chunkSizeWarningLimit: 1600,
      // Add commonjs options for better compatibility
      commonjsOptions: {
        transformMixedEsModules: true,
      },
      // Configure rollup options
      rollupOptions: {
        // Externalize node_modules
        external: ['lodash'],
        input: {
          main: path.resolve(__dirname, 'index.html'),
        },
        output: {
          entryFileNames: 'assets/[name]-[hash].js',
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash][extname]',
          globals: {
            lodash: '_',
          },
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
            mui: ['@mui/material', '@emotion/react', '@emotion/styled'],
            charts: ['lightweight-charts', 'recharts'],
          },
        },
      },
      // Enable/disable brotli compression
      brotliSize: true,
    },

    // Resolve configuration
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@components': path.resolve(__dirname, 'src/components'),
        '@services': path.resolve(__dirname, '../services'),  // Updated to point to root services directory
        '@pages': path.resolve(__dirname, 'src/pages'),
        '@utils': path.resolve(__dirname, 'src/utils'),
        '@assets': path.resolve(__dirname, 'src/assets'),
        '@hooks': path.resolve(__dirname, 'src/hooks'),
        '@contexts': path.resolve(__dirname, 'src/contexts'),
      },
      extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json'],
      // Add preserveSymlinks to handle symlinked node_modules
      preserveSymlinks: true,
    },

    // Server configuration
    server: {
      host: isDocker ? '0.0.0.0' : 'localhost',
      port: 3000,
      strictPort: true,
      open: !isDocker,
      proxy: {
        '/api': {
          target: isDocker ? 'http://backend:8000' : 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          secure: false,
          ws: true,
        },
      },
      fs: {
        // Allow serving files from one level up from the package root
        allow: ['..'],
      },
    },

    // Preview configuration
    preview: {
      port: 3000,
      open: true,
    },

    // Environment variables
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      'process.env': {},
      // This allows vitest to work without TypeScript errors
      'import.meta.vitest': 'undefined',
    },

    // CSS configuration
    css: {
      modules: {
        localsConvention: 'camelCaseOnly',
      },
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/styles/variables.scss";`,
        },
      },
    },

    // Optimize dependencies
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        '@mui/material',
        '@emotion/react',
        '@emotion/styled',
        'lightweight-charts',
        'lodash',  // Explicitly include lodash
      ],
      exclude: ['js-big-decimal'],
    },
  };
});
