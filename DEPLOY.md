# Quick Deploy Guide 🚀

## TL;DR - Fastest Way to Deploy

### Step 1: Deploy Backend (5 minutes)

1. Go to [railway.app](https://railway.app) → Sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `hack-knight` repository
4. Click "Add variables" and add:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_JWT_SECRET=your_jwt_secret
   STORAGE_BUCKET_NAME=food-images
   ENVIRONMENT=production
   ```
5. Click "Deploy"
6. **Copy the Railway URL** (e.g., `https://your-app.up.railway.app`)

### Step 2: Deploy Frontend (3 minutes)

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click "Pages" → "Create a project" → "Connect to Git"
3. Select `hack-knight` repository
4. Configure:
   ```
   Framework: Next.js
   Root directory: frontend
   Build command: npm run build
   Build output: .next
   ```
5. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=<paste-your-railway-url-from-step-1>
   ```
6. Click "Save and Deploy"

### Step 3: Done! ✅

Your app is live at:
- Frontend: `https://hack-knight-xxx.pages.dev`
- Backend: `https://your-app.up.railway.app`
- API Docs: `https://your-app.up.railway.app/docs`

---

## Alternative: Use Scripts

```bash
# Make scripts executable (one time)
chmod +x deploy-*.sh

# Deploy everything
./deploy-all.sh

# Or deploy individually
./deploy-railway.sh      # Backend only
./deploy-cloudflare.sh   # Frontend only
```

---

## Costs

| Service | Cost |
|---------|------|
| Cloudflare Pages | **FREE** ✅ |
| Railway | **$5/month** or free trial |
| Supabase | **FREE** tier (sufficient) |
| **Total** | **$0-5/month** |

---

## Custom Domain (Optional)

### Frontend Domain
1. In Cloudflare Pages → Custom domains
2. Add `app.yourdomain.com`
3. Cloudflare handles DNS automatically

### Backend Domain
1. In Cloudflare DNS
2. Add CNAME: `api.yourdomain.com` → `your-app.up.railway.app`
3. Update frontend env: `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`

---

## Troubleshooting

### Build fails on Cloudflare?
- Check Node version is set to 20
- Verify `frontend/` directory is correct
- Check build logs for errors

### Backend not responding?
- Verify environment variables in Railway
- Check Railway logs for errors
- Test backend URL directly: `<url>/health`

### CORS errors?
Update `backend/config/settings.py`:
```python
CORS_ORIGINS: list = ["*"]  # Or specific domains
```

---

## Need More Help?

📖 Full detailed guide: [docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md](docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md)

---

## Deployment Checklist

- [ ] Backend deployed to Railway
- [ ] Environment variables set
- [ ] Backend URL copied
- [ ] Frontend deployed to Cloudflare
- [ ] Frontend env variable set
- [ ] Test backend: `/health` endpoint
- [ ] Test frontend: opens in browser
- [ ] Test food upload (if ready)
- [ ] (Optional) Custom domains configured
- [ ] (Optional) Deploy ML model

---

**Questions?** Check the full guide or Railway/Cloudflare documentation!

