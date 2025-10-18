#!/bin/bash

# Complete Deployment Script
# Deploys both backend and frontend
# Usage: ./deploy-all.sh

echo "🚀 Complete Deployment - Nutrition Tracking App"
echo "================================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js first."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ git not found. Please install git first."
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# Option to deploy via GitHub (recommended)
echo "Deployment Options:"
echo "1. Deploy via GitHub (Recommended - automatic updates)"
echo "2. Deploy via CLI (Manual)"
read -p "Choose option (1 or 2): " DEPLOY_OPTION

if [ "$DEPLOY_OPTION" == "1" ]; then
    echo ""
    echo "📝 GitHub Deployment Steps:"
    echo ""
    echo "1. Push your code to GitHub:"
    echo "   git add ."
    echo "   git commit -m 'Prepare for deployment'"
    echo "   git push origin main"
    echo ""
    echo "2. Deploy Backend to Railway:"
    echo "   - Go to https://railway.app"
    echo "   - Sign up/Login with GitHub"
    echo "   - Click 'New Project'"
    echo "   - Select your repository"
    echo "   - Choose 'backend' folder"
    echo "   - Add environment variables (see docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md)"
    echo "   - Deploy and copy the URL"
    echo ""
    echo "3. Deploy Frontend to Cloudflare Pages:"
    echo "   - Go to https://dash.cloudflare.com"
    echo "   - Click 'Pages' → 'Create a project'"
    echo "   - Connect to GitHub"
    echo "   - Select your repository"
    echo "   - Set root directory: 'frontend'"
    echo "   - Set build command: 'npm run build'"
    echo "   - Set output directory: '.next'"
    echo "   - Add environment variable:"
    echo "     NEXT_PUBLIC_API_URL=<your-railway-backend-url>"
    echo "   - Click 'Save and Deploy'"
    echo ""
    echo "📖 Full guide: docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md"
    
elif [ "$DEPLOY_OPTION" == "2" ]; then
    echo ""
    echo "Starting CLI deployment..."
    
    # Deploy backend
    echo ""
    echo "Step 1: Deploy Backend"
    read -p "Deploy backend to Railway? (y/n): " DEPLOY_BACKEND
    
    if [ "$DEPLOY_BACKEND" == "y" ]; then
        ./deploy-railway.sh
        read -p "Enter your Railway backend URL: " BACKEND_URL
    else
        read -p "Enter your existing backend URL: " BACKEND_URL
    fi
    
    # Deploy frontend
    echo ""
    echo "Step 2: Deploy Frontend"
    read -p "Deploy frontend to Cloudflare Pages? (y/n): " DEPLOY_FRONTEND
    
    if [ "$DEPLOY_FRONTEND" == "y" ]; then
        echo "$BACKEND_URL" | ./deploy-cloudflare.sh
    fi
    
    echo ""
    echo "✅ Deployment complete!"
else
    echo "Invalid option. Exiting."
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 Resources:"
echo "  - Deployment Guide: docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md"
echo "  - Railway Dashboard: https://railway.app"
echo "  - Cloudflare Dashboard: https://dash.cloudflare.com"
echo "  - API Documentation: <your-backend-url>/docs"

