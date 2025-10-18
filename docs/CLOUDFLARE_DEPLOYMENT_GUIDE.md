# Cloudflare Deployment Guide

## Overview

This guide covers deploying your nutrition tracking app with a **hybrid approach**:
- ✅ **Frontend (Next.js)** → Cloudflare Pages
- ⚠️ **Backend (FastAPI)** → Alternative platform (Cloudflare doesn't support Python)
- 🗄️ **Database** → Supabase (already external)
- 🖼️ **Images** → Supabase Storage (already external)
- 🤖 **ML Model** → Separate deployment

---

## ⚠️ Important: Cloudflare Limitations

### What Cloudflare Supports
- ✅ Static sites and frontend frameworks (Pages)
- ✅ JavaScript/TypeScript serverless functions (Workers)
- ✅ CDN and edge caching
- ✅ Custom domains and SSL

### What Cloudflare Doesn't Support
- ❌ Python backend (FastAPI)
- ❌ Long-running containers
- ❌ Traditional server applications

### Recommendation
**Deploy frontend on Cloudflare Pages, backend elsewhere**

---

## 📦 Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│ Cloudflare Pages (Frontend)                    │
│ - Next.js static export or SSR                 │
│ - Domain: app.yourdomain.com                    │
└─────────────────┬───────────────────────────────┘
                  │ API calls
                  ↓
┌─────────────────────────────────────────────────┐
│ Backend Platform (FastAPI)                      │
│ Options:                                        │
│ - Railway  (Recommended - Easy)                │
│ - Render   (Good free tier)                    │
│ - Fly.io   (Fast edge deployment)              │
│ - Heroku   (Popular, paid)                     │
│ Domain: api.yourdomain.com                      │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────┴────────┐
         ↓                 ↓
┌──────────────┐  ┌──────────────┐
│ Supabase     │  │ ML Model     │
│ (Database)   │  │ (Separate)   │
└──────────────┘  └──────────────┘
```

---

## Part 1: Deploy Frontend to Cloudflare Pages

### Option A: Deploy via GitHub (Recommended)

#### Step 1: Push to GitHub
```bash
cd /Users/zhuolin/Desktop/hack-knight
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### Step 2: Connect to Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click **Pages** in sidebar
3. Click **Create a project**
4. Click **Connect to Git**
5. Select your repository: `hack-knight`
6. Configure build settings:

**Build Settings:**
```
Framework preset: Next.js
Build command: npm run build
Build output directory: .next
Root directory: frontend
Node version: 20
```

**Environment Variables:**
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

7. Click **Save and Deploy**

#### Step 3: Wait for Build
- First deployment takes 2-5 minutes
- Cloudflare will provide a URL: `https://hack-knight-xxx.pages.dev`

#### Step 4: Add Custom Domain (Optional)
1. In Pages project, go to **Custom domains**
2. Click **Set up a custom domain**
3. Enter: `app.yourdomain.com`
4. Follow DNS setup instructions
5. SSL certificate auto-provisioned

---

### Option B: Deploy via Wrangler CLI

#### Step 1: Install Wrangler
```bash
npm install -g wrangler
```

#### Step 2: Login
```bash
wrangler login
```

#### Step 3: Configure Pages

Create `frontend/wrangler.toml`:
```toml
name = "nutrition-app"
compatibility_date = "2024-01-01"

[site]
bucket = ".next"

[build]
command = "npm run build"
cwd = "."

[env.production]
vars = { NEXT_PUBLIC_API_URL = "https://your-backend-url.com" }
```

#### Step 4: Deploy
```bash
cd frontend
npm run build
wrangler pages deploy .next
```

---

## Part 2: Deploy Backend (FastAPI)

Since Cloudflare doesn't support Python, here are the best alternatives:

### Option 1: Railway (Recommended - Easiest)

#### Why Railway?
- ✅ Free tier available
- ✅ Easy Python/Docker deployment
- ✅ Automatic HTTPS
- ✅ Environment variables
- ✅ One-click deploy

#### Step 1: Create Railway Account
Go to [railway.app](https://railway.app) and sign up

#### Step 2: Install Railway CLI
```bash
npm install -g @railway/cli
```

#### Step 3: Login
```bash
railway login
```

#### Step 4: Create Project
```bash
cd /Users/zhuolin/Desktop/hack-knight/backend
railway init
```

#### Step 5: Add Environment Variables
```bash
railway variables set SUPABASE_URL=your-supabase-url
railway variables set SUPABASE_KEY=your-supabase-key
railway variables set SUPABASE_JWT_SECRET=your-jwt-secret
railway variables set STORAGE_BUCKET_NAME=food-images
railway variables set ML_SERVICE_URL=your-ml-service-url
railway variables set GEMINI_API_KEY=your-gemini-key  # Optional
railway variables set ENVIRONMENT=production
```

#### Step 6: Deploy
```bash
railway up
```

#### Step 7: Get URL
```bash
railway domain
```

Your backend will be at: `https://your-app.up.railway.app`

#### Step 8: Update Frontend
Update Cloudflare Pages environment variable:
```
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

---

### Option 2: Render.com (Good Free Tier)

#### Step 1: Create Account
Go to [render.com](https://render.com) and sign up

#### Step 2: New Web Service
1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Select `backend` folder

#### Step 3: Configure
```
Name: nutrition-app-backend
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Instance Type: Free
```

#### Step 4: Environment Variables
Add in Render dashboard:
```
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_JWT_SECRET=...
STORAGE_BUCKET_NAME=food-images
ML_SERVICE_URL=...
GEMINI_API_KEY=...
ENVIRONMENT=production
```

#### Step 5: Deploy
Click **Create Web Service** → automatic deployment

Your backend will be at: `https://nutrition-app-backend.onrender.com`

---

### Option 3: Fly.io (Fast Edge Deployment)

#### Step 1: Install Fly CLI
```bash
curl -L https://fly.io/install.sh | sh
```

#### Step 2: Login
```bash
fly auth login
```

#### Step 3: Create App
```bash
cd /Users/zhuolin/Desktop/hack-knight/backend
fly launch
```

Answer prompts:
- App name: `nutrition-app-backend`
- Region: Choose closest to your users
- Database: No (using Supabase)
- Deploy now: No

#### Step 4: Configure fly.toml
```toml
app = "nutrition-app-backend"
primary_region = "sjc"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  ENVIRONMENT = "production"

[[services]]
  protocol = "tcp"
  internal_port = 8000

  [[services.ports]]
    port = 80
    handlers = ["http"]
  
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

#### Step 5: Set Secrets
```bash
fly secrets set SUPABASE_URL=your-url
fly secrets set SUPABASE_KEY=your-key
fly secrets set SUPABASE_JWT_SECRET=your-secret
fly secrets set STORAGE_BUCKET_NAME=food-images
fly secrets set ML_SERVICE_URL=your-ml-url
fly secrets set GEMINI_API_KEY=your-key
```

#### Step 6: Deploy
```bash
fly deploy
```

Your backend will be at: `https://nutrition-app-backend.fly.dev`

---

## Part 3: Deploy ML Model

Your custom ML model needs separate deployment.

### Option 1: Railway

```bash
cd /path/to/your/ml-service
railway init
railway up
railway domain
```

### Option 2: Render

Create new Web Service, point to ML model repository

### Option 3: Hugging Face Spaces

1. Create account at [huggingface.co](https://huggingface.co)
2. Create new Space
3. Upload model and inference code
4. Get endpoint URL

### Option 4: Google Cloud Run

```bash
gcloud run deploy ml-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Part 4: Configure Custom Domains

### Frontend Domain (Cloudflare)

1. In Cloudflare Pages project → **Custom domains**
2. Add: `app.yourdomain.com`
3. Update DNS:
   ```
   CNAME app yourdomain.pages.dev
   ```

### Backend Domain (Using Cloudflare DNS)

Assuming backend is on Railway at `your-app.up.railway.app`:

1. Go to Cloudflare DNS settings
2. Add CNAME record:
   ```
   Type: CNAME
   Name: api
   Target: your-app.up.railway.app
   Proxy status: Proxied (orange cloud)
   ```
3. Update frontend environment:
   ```
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   ```

---

## Part 5: CORS Configuration

Update backend CORS to allow your Cloudflare domain:

**backend/config/settings.py:**
```python
CORS_ORIGINS: list = [
    "http://localhost:3000",
    "https://hack-knight-xxx.pages.dev",  # Cloudflare Pages URL
    "https://app.yourdomain.com",  # Your custom domain
]
```

Or allow all (less secure):
```python
CORS_ORIGINS: list = ["*"]
```

Redeploy backend after changes.

---

## Part 6: Environment Variables Summary

### Frontend (Cloudflare Pages)
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Backend (Railway/Render/Fly.io)
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
STORAGE_BUCKET_NAME=food-images
ML_SERVICE_URL=https://your-ml-model.com/api
GEMINI_API_KEY=your-gemini-key  # Optional
GEMINI_MODEL=gemini-pro
ENVIRONMENT=production
```

---

## Part 7: CI/CD Setup

### Auto-Deploy on Git Push

#### Cloudflare Pages (Frontend)
Automatically deploys on every push to main branch ✅

#### Railway (Backend)
```bash
# Enable auto-deploy
railway up --detach

# Now every git push triggers deployment
```

#### GitHub Actions (Alternative)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: nutrition-app
          directory: frontend/.next
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
  
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: railway/cli@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up
```

---

## Part 8: Monitoring & Logs

### Cloudflare Pages
- View logs in Cloudflare Dashboard → Pages → your-project → Deployments
- Real-time analytics available

### Railway
```bash
railway logs
```

Or view in Railway dashboard

### Render
- View logs in Render dashboard → your-service → Logs

### Fly.io
```bash
fly logs
```

---

## Part 9: Cost Estimate

### Free Tier Options

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Cloudflare Pages** | ✅ Free | Unlimited requests, 500 builds/month |
| **Railway** | $5 credit/month | ~1 small app |
| **Render** | ✅ Free | 750 hours/month (1 instance) |
| **Fly.io** | $5 credit/month | 3 shared-cpu VMs |
| **Supabase** | ✅ Free | 500MB database, 1GB storage |

**Total Monthly Cost: $0-10** (depending on platform choice)

### Paid Recommendations

For production with higher traffic:
- Cloudflare Pages: Free
- Railway Hobby: $5/month
- Supabase Pro: $25/month
- **Total: ~$30/month**

---

## Part 10: Testing Deployment

### Step 1: Test Frontend
```bash
curl https://app.yourdomain.com
# Should return Next.js HTML
```

### Step 2: Test Backend
```bash
curl https://api.yourdomain.com/health
# Should return: {"status": "healthy", ...}
```

### Step 3: Test API Docs
Visit: `https://api.yourdomain.com/docs`

### Step 4: Test Full Flow
1. Open `https://app.yourdomain.com`
2. Try uploading a food image
3. Check if it connects to backend
4. Verify database updates in Supabase

---

## Part 11: Troubleshooting

### Frontend Build Fails
```bash
# Check Node version
node --version  # Should be 20+

# Test build locally
cd frontend
npm run build
```

### Backend Not Responding
```bash
# Check logs
railway logs  # or render logs, fly logs

# Test locally
cd backend
uvicorn main:app --reload
```

### CORS Errors
Update `CORS_ORIGINS` in `backend/config/settings.py`

### Database Connection Failed
- Verify `SUPABASE_URL` and `SUPABASE_KEY`
- Check Supabase dashboard for connection errors

---

## Quick Start: Fastest Deployment

### 1. Deploy Backend to Railway (5 min)
```bash
cd backend
railway login
railway init
railway variables set SUPABASE_URL=xxx
railway variables set SUPABASE_KEY=xxx
railway variables set SUPABASE_JWT_SECRET=xxx
railway variables set STORAGE_BUCKET_NAME=food-images
railway up
railway domain  # Get your backend URL
```

### 2. Deploy Frontend to Cloudflare Pages (3 min)
1. Push code to GitHub
2. Go to Cloudflare Dashboard → Pages
3. Connect repository
4. Set environment: `NEXT_PUBLIC_API_URL=https://your-railway-url`
5. Deploy

### 3. Done! 🎉
- Frontend: `https://hack-knight-xxx.pages.dev`
- Backend: `https://your-app.up.railway.app`

---

## Alternative: All-Railway Deployment

You can deploy **both** frontend and backend on Railway:

```bash
# Deploy backend
cd backend
railway init
railway up

# Deploy frontend (in new project)
cd ../frontend
railway init
railway up
```

Benefits:
- Everything in one place
- Easier management
- Single platform

Drawbacks:
- Not using Cloudflare's global CDN
- Slightly higher cost

---

## Summary

### Recommended Setup

✅ **Frontend**: Cloudflare Pages (free, fast, global CDN)  
✅ **Backend**: Railway (easy, $5/month or free tier)  
✅ **Database**: Supabase (free tier sufficient)  
✅ **ML Model**: Railway/Render (deploy separately)

### Deployment Checklist

- [ ] Push code to GitHub
- [ ] Deploy backend to Railway
- [ ] Get backend URL
- [ ] Deploy frontend to Cloudflare Pages
- [ ] Set `NEXT_PUBLIC_API_URL` environment variable
- [ ] Configure custom domains
- [ ] Update CORS settings
- [ ] Test full application
- [ ] Set up monitoring
- [ ] Deploy ML model (when ready)

---

**Need help with any specific step? Let me know!** 🚀

