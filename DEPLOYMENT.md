# Deploy Django Backend to Production

## Option 1: Railway (Recommended - Easiest)

1. **Create Railway Account:**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Deploy:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository
   - Select the `backend` folder as the root directory
   - Railway will auto-detect it's a Python project

3. **Set Environment Variables:**
   - In Railway dashboard, go to "Variables" tab
   - Add these environment variables:
     ```
     SECRET_KEY=your-secret-key-here (generate a random string)
     DEBUG=False
     ALLOWED_HOSTS=your-railway-url.railway.app
     EMAIL_HOST_USER=info@primefixusa.com
     EMAIL_HOST_PASSWORD=Primefixusa@11274
     DEFAULT_FROM_EMAIL=info@primefixusa.com
     RECIPIENT_EMAIL=info@primefixusa.com
     CORS_ALLOW_ALL_ORIGINS=True
     ```

4. **Generate Secret Key:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Update Frontend:**
   - Get your Railway URL (something like: `your-app.up.railway.app`)
   - Update `index.html` line 728 to use: `https://your-app.up.railway.app/api/contact/`

---

## Option 2: Render (Free Tier Available)

1. **Create Render Account:**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Set these settings:
     - **Root Directory:** `backend`
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn primefix_backend.wsgi`

3. **Set Environment Variables:**
   - Go to "Environment" tab
   - Add the same variables as Railway (see above)

4. **Update Frontend:**
   - Get your Render URL (something like: `your-app.onrender.com`)
   - Update `index.html` line 728 to use: `https://your-app.onrender.com/api/contact/`

---

## After Deployment

1. **Update Frontend API URL:**
   - Open `index.html`
   - Find line 728: `var apiUrl = 'http://localhost:8000/api/contact/';`
   - Replace with your deployed backend URL (e.g., `https://your-app.railway.app/api/contact/`)

2. **Test:**
   - Submit the contact form on your Vercel site
   - Check `info@primefixusa.com` inbox for the email

---

## Security Notes

- Never commit `.env` files to Git
- Use environment variables for sensitive data (passwords, keys)
- Set `DEBUG=False` in production
- Keep `SECRET_KEY` secret and random

