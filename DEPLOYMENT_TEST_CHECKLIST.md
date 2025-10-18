# Deployment Test Checklist

## ✅ What Was Fixed

### Frontend Fixes
1. **Removed `output: 'standalone'`** - Not compatible with Cloudflare Pages
2. **Added error boundaries** - Shows user-friendly errors instead of white screen
3. **Improved Supabase client** - Gracefully handles missing env variables
4. **Added error logging** - Console shows what's misconfigured

### Backend Fixes  
1. **Updated CORS settings** - Now allows all origins (configure for your domain)

---

## 🔍 Testing Instructions

### Step 1: Check Frontend Deployment
After Cloudflare auto-deploys the latest commit (`4d3004e`):

1. **Open your Cloudflare Pages URL**
2. **Open Browser DevTools** (F12 or Cmd+Option+I)
3. **Check the Console tab** for errors

**What to look for:**
- ✅ If page loads: Great! Continue to Step 2
- ⚠️ If you see: `"Supabase environment variables are not configured!"` → Go to **Fix A**
- ❌ If still white screen → Check console for other errors

### Step 2: Check Backend Connection
1. **In the browser console**, type:
   ```javascript
   fetch(process.env.NEXT_PUBLIC_API_URL || 'YOUR_BACKEND_URL')
     .then(r => r.json())
     .then(d => console.log('Backend response:', d))
   ```

**What to look for:**
- ✅ You see: `Backend response: {message: "Welcome to Food App API! 🍎", ...}` → Great!
- ❌ Network error / CORS error → Go to **Fix B**
- ❌ `NEXT_PUBLIC_API_URL is undefined` → Go to **Fix C**

### Step 3: Test Image Upload
1. Click "Upload Image" or "Take Photo"
2. Select/take a food image
3. Wait for processing

**What to look for:**
- ✅ Upload succeeds, meal appears in list → Perfect!
- ❌ Upload fails → Check console for error details

### Step 4: Test Chatbot
1. Click the chat button (bottom right)
2. Send a message like "What should I eat?"

**What to look for:**
- ✅ Bot responds with nutrition advice → Working!
- ❌ Error → Check if GEMINI_API_KEY is set in backend

---

## 🔧 Common Fixes

### Fix A: Configure Supabase Environment Variables

**In Cloudflare Pages Dashboard:**
1. Go to your project → **Settings** → **Environment variables**
2. Add these variables (for both Production and Preview):
   ```
   NEXT_PUBLIC_SUPABASE_URL = https://xxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY = your-anon-key-here
   ```
3. Get values from: [Supabase Dashboard](https://supabase.com/dashboard) → Your Project → Settings → API
4. **Retry deployment** after adding variables

### Fix B: Backend Not Accessible

**Check if backend is deployed:**
1. Find your backend URL (Railway/Render/etc)
2. Open `https://YOUR-BACKEND-URL/health` in browser
3. Should see: `{"status": "healthy", ...}`

**If not working:**
- Backend might not be deployed yet
- Deploy backend using instructions in `/docs/DEPLOY.md`
- Popular options: Railway (easy), Render (free tier), Fly.io

### Fix C: Configure Backend URL

**In Cloudflare Pages Dashboard:**
1. Go to your project → **Settings** → **Environment variables**
2. Add:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend.up.railway.app
   ```
   (Replace with your actual backend URL)
3. **Retry deployment**

### Fix D: CORS Errors

**If you see CORS errors in browser console:**

The backend CORS is now set to allow all origins (`*`). If you still have issues:

1. **Check backend logs** - see if requests are reaching it
2. **Verify backend URL** - make sure it's accessible
3. **For production** - update `backend/config/settings.py` to only allow your domain:
   ```python
   CORS_ORIGINS: list = [
       "https://your-app.pages.dev",
       "https://your-custom-domain.com"
   ]
   ```

---

## 📋 Required Environment Variables

### Frontend (Cloudflare Pages)
```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...
NEXT_PUBLIC_API_URL=https://your-backend.com
```

### Backend (Railway/Render/etc)
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxx...  # Service role key (different from anon!)
SUPABASE_JWT_SECRET=your-jwt-secret
STORAGE_BUCKET_NAME=food-images
GEMINI_API_KEY=your-gemini-api-key  # Optional, for chatbot
ENVIRONMENT=production
```

---

## 🎯 Next Steps

1. **Wait for Cloudflare to deploy** the latest commit (`4d3004e`)
2. **Open the deployed URL** and check browser console
3. **Follow the fixes above** based on what you see
4. **Test all features** using the checklist above

---

## 📞 Getting Help

**If you're still seeing issues:**
1. Share the **browser console errors** (screenshot or text)
2. Share your **Cloudflare Pages URL**
3. Confirm if **backend is deployed** and share its URL
4. Confirm **environment variables are set** in Cloudflare dashboard

**Quick Test URLs:**
- Frontend health: `https://your-app.pages.dev/`
- Backend health: `https://your-backend.com/health`
- Backend docs: `https://your-backend.com/docs`

