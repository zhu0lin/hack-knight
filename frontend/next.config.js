/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',  // Static export for Cloudflare Pages
  images: {
    unoptimized: true,  // Required for static export
  },
}

module.exports = nextConfig

