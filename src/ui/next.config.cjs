/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  //distDir: 'out',
  images: {
    unoptimized: true,
    domains: ['localhost'] // Add any domains from which you'll load images
  },
  async rewrites() {
    return [
      // Proxy API requests to your backend
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*', // Proxy to your backend
      },
    ];
  },
}

module.exports = nextConfig

