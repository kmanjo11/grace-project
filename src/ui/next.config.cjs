/** @type {import('next').NextConfig} */

const isProduction = process.env.NODE_ENV === 'production';
const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || (isProduction ? 'http://localhost:9000' : '/api');

module.exports = {
  output: 'export',
  trailingSlash: true,
  reactStrictMode: true,
  distDir: 'out',
  images: {
    unoptimized: true
  },
  env: {
    // Set NEXT_PUBLIC_API_URL for all environments
    NEXT_PUBLIC_API_URL: apiBaseUrl,
  },
  // API rewrites (for development mode only, not used in static export)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:9000/api/:path*',
      },
    ];
  },
};
