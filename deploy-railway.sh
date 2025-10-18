#!/bin/bash

# Railway Deployment Script for Backend
# Usage: ./deploy-railway.sh

echo "🚀 Deploying Backend to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Navigate to backend directory
cd backend || exit

# Check if already initialized
if [ ! -f "railway.json" ]; then
    echo "📝 Initializing Railway project..."
    railway init
fi

# Set environment variables
echo "🔧 Setting environment variables..."
echo "Please enter your Supabase credentials:"

read -p "SUPABASE_URL: " SUPABASE_URL
read -p "SUPABASE_KEY: " SUPABASE_KEY
read -p "SUPABASE_JWT_SECRET: " SUPABASE_JWT_SECRET
read -p "STORAGE_BUCKET_NAME (default: food-images): " STORAGE_BUCKET_NAME
STORAGE_BUCKET_NAME=${STORAGE_BUCKET_NAME:-food-images}

read -p "ML_SERVICE_URL (optional, press enter to skip): " ML_SERVICE_URL
read -p "GEMINI_API_KEY (optional, press enter to skip): " GEMINI_API_KEY

# Set variables
railway variables set SUPABASE_URL="$SUPABASE_URL"
railway variables set SUPABASE_KEY="$SUPABASE_KEY"
railway variables set SUPABASE_JWT_SECRET="$SUPABASE_JWT_SECRET"
railway variables set STORAGE_BUCKET_NAME="$STORAGE_BUCKET_NAME"
railway variables set ENVIRONMENT="production"

if [ -n "$ML_SERVICE_URL" ]; then
    railway variables set ML_SERVICE_URL="$ML_SERVICE_URL"
fi

if [ -n "$GEMINI_API_KEY" ]; then
    railway variables set GEMINI_API_KEY="$GEMINI_API_KEY"
    railway variables set GEMINI_MODEL="gemini-pro"
fi

# Deploy
echo "🚀 Deploying to Railway..."
railway up

# Get domain
echo ""
echo "✅ Deployment complete!"
echo "🌐 Getting your backend URL..."
railway domain

echo ""
echo "📝 Next steps:"
echo "1. Copy the URL above"
echo "2. Set it as NEXT_PUBLIC_API_URL in Cloudflare Pages"
echo "3. Deploy your frontend"

cd ..

