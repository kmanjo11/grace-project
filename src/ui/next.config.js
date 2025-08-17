/** @type {import('next').NextConfig} */

const isProduction = process.env.NODE_ENV === 'production';
const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '';

const nextConfig = {
  trailingSlash: false,
  reactStrictMode: true,
  images: {
    unoptimized: true
  },
  env: {
    // Set NEXT_PUBLIC_API_URL for all environments
    NEXT_PUBLIC_API_URL: apiBaseUrl,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:9000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
