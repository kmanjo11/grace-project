import { defineConfig, loadEnv, type PluginOption } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { VitePWA } from 'vite-plugin-pwa';

// Type for the visualizer plugin
type VisualizerPlugin = (options?: any) => PluginOption;

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
          plugins: [
            ['@emotion/babel-plugin', { sourceMap: true }],
            'babel-plugin-macros'
          ],
        },
      }) as PluginOption,
      // Visualize bundle size
      isProduction && (visualizer as unknown as VisualizerPlugin)({
        open: false,
        gzipSize: true,
        brotliSize: true,
      }) as PluginOption,
      // PWA support - simplified configuration
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
        strategies: 'generateSW',
        injectRegister: 'auto',
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg}']
        },
        manifest: {
          name: 'Grace Trading Platform',
          short_name: 'Grace',
          description: 'Advanced trading platform with Mango V3 integration',
          theme_color: '#1976d2',
          start_url: '/',
          display: 'standalone',
          background_color: '#ffffff',
          icons: [
            {
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png',
              purpose: 'any maskable'
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any maskable'
            },
          ],
        },
      }),
    ].filter(Boolean),

    // Base public path when served in production
    base: '/',

    // Root directory - use absolute path to src/ui
    root: __dirname,



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
        external: (id) => {
          // Externalize all @mui/* packages
          if (id.startsWith('@mui/')) return true;
          
          // Externalize react and related
          if (id.startsWith('react') || id === 'react' || id === 'react-dom') return true;
          
          // Existing externals
          const existingExternals = [
            'lodash',
            'react-router',
            'react-router-dom',
            '@babel/runtime/helpers/extends',
            '@babel/runtime/helpers/objectWithoutProperties',
            '@babel/runtime/helpers/classCallCheck',
            '@babel/runtime/helpers/createClass',
            '@babel/runtime/helpers/defineProperty',
            '@babel/runtime/helpers/inherits',
            '@babel/runtime/helpers/possibleConstructorReturn',
            '@babel/runtime/helpers/getPrototypeOf',
            '@babel/runtime/helpers/assertThisInitialized',
            '@babel/runtime/helpers/typeof',
            '@babel/runtime/helpers/asyncToGenerator',
            '@babel/runtime/regenerator',
            'fancy-canvas',
            'react-is',
            '@mui/styled-engine',
            // Add any other specific packages you want to explicitly externalize
          ];
          
          // If it's in our explicit list, externalize it
          if (existingExternals.includes(id)) return true;
          
          // If it's from node_modules, externalize it
          if (id.includes('node_modules')) return true;
          
          // If it's a scoped package (starts with @), externalize it
          if (id.startsWith('@') && id.includes('/')) return true;
          
          // For all other cases, let Vite handle it
          return false;
        },
        input: path.resolve(__dirname, 'index.html'),
        output: {
          entryFileNames: 'assets/[name]-[hash].js',
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash][extname]',
          globals: {
            lodash: 'lodash',
          },
          manualChunks: {
            // All external dependencies are now handled by the external config
            // Keeping this empty object to maintain the configuration structure
            // but you could potentially remove manualChunks entirely if not needed
          },
        },
      },
      // Enable/disable brotli compression
      brotliSize: true,
    },

    // Resolve configuration
    resolve: {
      // Check root node_modules first, then local node_modules
      modules: [
        path.resolve(__dirname, '../../node_modules'), // Root node_modules
        path.resolve(__dirname, 'node_modules')  // Local node_modules (fallback)
      ],
      alias: [
        // Emotion JSX runtime resolution
        {
          find: '@emotion/react/jsx-runtime',
          replacement: require.resolve('@emotion/react/jsx-runtime')
        },
        // Keep existing path aliases
        {
          find: /^@\/(.*)/,
          replacement: path.resolve(__dirname, '$1')
        },
        // Explicit aliases for better performance and to avoid catch-all issues
        // Keep explicit aliases for better performance
        {
          find: '@components',
          replacement: path.resolve(__dirname, 'components')
        },
        {
          find: '@services',
          replacement: path.resolve(__dirname, '../services')
        },
        {
          find: '@pages',
          replacement: path.resolve(__dirname, 'pages')
        },
        {
          find: '@utils',
          replacement: path.resolve(__dirname, 'utils')
        },
        {
          find: '@assets',
          replacement: path.resolve(__dirname, 'assets')
        },
        {
          find: '@hooks',
          replacement: path.resolve(__dirname, 'hooks')
        },
        {
          find: '@context',
          replacement: path.resolve(__dirname, '../context')
        },
        {
          find: '@emotion/react/jsx-runtime',
          replacement: new URL('../../node_modules/@emotion/react/jsx-runtime/dist/emotion-react-jsx-runtime.cjs.js', import.meta.url).pathname
        },
        {
          find: '@emotion/react/jsx-dev-runtime',
          replacement: new URL('../../node_modules/@emotion/react/jsx-runtime/dist/emotion-react-jsx-runtime.development.cjs.js', import.meta.url).pathname
        },
      ],
      extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json'],
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
        allow: ['../../'],  
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

    // Optimize dependencies for better build performance
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        'react-router',
        '@mui/material',
        '@emotion/react',
        '@emotion/react/jsx-runtime',
        '@emotion/styled',
        '@emotion/cache',
        'lightweight-charts',
        'lodash',
      ],
      exclude: ['js-big-decimal'],
      esbuildOptions: {
        // Enable esbuild's tree shaking
        treeShaking: true,
        // Better compatibility
        define: { global: 'globalThis' },
        // Modern JS target
        target: 'es2020',
        supported: { bigint: true },
        // Enable concurrent builds
        incremental: true
      }
    },
  };
});
