# Quick Deployment Guide

## Step 1: Choose Platform

**Railway (Recommended):**
- Free tier available
- Easy setup
- Go to: https://railway.app

**Render (Alternative):**
- Free tier available  
- Go to: https://render.com

---

## Step 2: Deploy to Railway

1. **Sign up:** https://railway.app (use GitHub to sign in)

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Set **Root Directory** to: `backend`

3. **Add Environment Variables:**
   Go to "Variables" tab and add:
   ```
   SECRET_KEY=<generate-secret-key-below>
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app
   EMAIL_HOST_USER=info@primefixusa.com
   EMAIL_HOST_PASSWORD=Primefixusa@11274
   DEFAULT_FROM_EMAIL=info@primefixusa.com
   RECIPIENT_EMAIL=info@primefixusa.com
   CORS_ALLOW_ALL_ORIGINS=True
   ```

4. **Generate Secret Key:**
   Run this command in your terminal:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Copy the output and use it as SECRET_KEY

5. **Deploy:**
   Railway will automatically detect it's Python and deploy

6. **Get Your URL:**
   - After deployment, Railway will give you a URL like: `your-app.up.railway.app`
   - Copy this URL

---

## Step 3: Update Frontend

1. Open `index.html`
2. Find line 728 (or search for `var apiUrl`)
3. Replace `http://localhost:8000/api/contact/` with:
   ```
   https://your-app.up.railway.app/api/contact/
   ```
   (Use your actual Railway URL)

4. Commit and push to GitHub
5. Vercel will automatically redeploy

---

## Step 4: Test

1. Go to your Vercel website
2. Fill out the contact form
3. Submit it
4. Check `info@primefixusa.com` inbox

---

## Done! 🎉

Your backend is now online and working with your Vercel frontend!

