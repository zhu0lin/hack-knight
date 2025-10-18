/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Remove 'output: standalone' for Cloudflare Pages compatibility
  // Cloudflare Pages handles the build output automatically
}

module.exports = nextConfig

