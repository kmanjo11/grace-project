/// <reference types="vite/client" />

// Emotion JSX support
declare module '@emotion/react/jsx-runtime' {
  import { JSX } from 'react';
  export { jsx, jsxs, Fragment } from '@emotion/react';
  export type { JSX };
}

// Environment variables
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_WS_URL?: string;
  readonly VITE_ENV?: 'development' | 'production' | 'test';
  // Add other environment variables here as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
