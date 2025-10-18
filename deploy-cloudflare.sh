#!/bin/bash

# Cloudflare Pages Deployment Script for Frontend
# Usage: ./deploy-cloudflare.sh

echo "🚀 Deploying Frontend to Cloudflare Pages..."

# Check if Wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI not found. Installing..."
    npm install -g wrangler
fi

# Navigate to frontend directory
cd frontend || exit

# Get backend URL
read -p "Enter your backend URL (e.g., https://your-app.up.railway.app): " BACKEND_URL

# Create or update .env.production
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > .env.production

# Build the project
echo "📦 Building frontend..."
npm install
npm run build

# Login to Cloudflare (if not already)
echo "🔐 Logging in to Cloudflare..."
wrangler login

# Deploy to Pages
echo "🚀 Deploying to Cloudflare Pages..."
wrangler pages deploy .next --project-name=nutrition-app

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your app is live!"
echo ""
echo "📝 Optional: Add custom domain in Cloudflare Dashboard"
echo "   Pages → nutrition-app → Custom domains"

cd ..

