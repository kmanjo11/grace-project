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
        jsxRuntime: 'automatic',
        babel: {
          plugins: [
            ['@emotion/babel-plugin', { 
              sourceMap: true,
              autoLabel: 'dev-only',
              labelFormat: '[local]',
              cssPropOptimization: true
            }],
            'babel-plugin-macros'
          ]
        }
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
        // Externalize packages as required by build errors
        external: (id) => {
          // Packages that MUST be externalized (as required by error messages)
          const requiredExternals = [
            'react-is', // REQUIRED: Material-UI needs this externalized
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
            '@mui/styled-engine',
          ];
          
          // If it's in our required externals list, externalize it
          if (requiredExternals.includes(id)) return true;
          
          // Externalize all @mui/* packages
          if (id.startsWith('@mui/')) return true;
          
          // Externalize react and related packages
          if (id.startsWith('react') || id === 'react' || id === 'react-dom') return true;
          
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
            'react': 'React',
            'react-dom': 'ReactDOM',
            'react-is': 'ReactIs',
            'lodash': 'lodash',
          },
          manualChunks: {
            // Keep manual chunks empty since we're externalizing most dependencies
          },
        },
      },
      // Enable/disable brotli compression
      brotliSize: true,
    },

    // Resolve configuration - CLEAN (NO JSX RUNTIME ALIASES)
    resolve: {
      // Check root node_modules first, then local node_modules
      modules: [
        path.resolve(__dirname, '../../node_modules'), // Root node_modules
        path.resolve(__dirname, 'node_modules'),  // Local node_modules (fallback)
      ],
      alias: [
        // Keep existing path aliases - NO EMOTION JSX RUNTIME ALIASES
        {
          find: /^@\/(.*)/,
          replacement: path.resolve(__dirname, '$1')
        },
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
        // NO JSX RUNTIME ALIASES - Let React plugin handle JSX runtime automatically
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
      // Include packages for development optimization (not used in production build)
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        'react-router',
        '@mui/material',
        '@emotion/react',
        '@emotion/styled',
        '@emotion/cache',
        'lightweight-charts',
        'lodash',
      ],
      exclude: ['js-big-decimal'],
      esbuildOptions: {
        // JSX configuration - let React plugin handle JSX runtime automatically
        jsx: 'automatic',
        // Better compatibility
        define: { global: 'globalThis' },
        // Modern JS target
        target: 'es2020',
        supported: { bigint: true },
        // Performance optimizations
        treeShaking: true,
      }
    },
  };
});

