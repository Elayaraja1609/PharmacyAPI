# Alternative Deployment Options

If Deta Space is experiencing issues, here are alternative free hosting options for your Flask backend:

## Option 1: Render (Recommended Alternative)

### Why Render?
- ✅ Free tier available
- ✅ Easy deployment
- ✅ Automatic HTTPS
- ✅ Free PostgreSQL (if you want to switch later)
- ✅ No credit card required for free tier

### Deployment Steps:

1. **Sign up at [Render.com](https://render.com)**

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or use manual deploy)
   - Select the repository

3. **Configure Service:**
   ```
   Name: pharmacy-backend
   Region: Choose closest to you
   Branch: main (or your default branch)
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```

4. **Add Environment Variables:**
   - `MONGO_URI`: Your MongoDB Atlas connection string
   - `JWT_SECRET_KEY`: Your secret key
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`
   - `PORT`: `5000` (Render sets this automatically, but include it)

5. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Get your URL: `https://pharmacy-backend.onrender.com`

### Render Free Tier Notes:
- Spins down after 15 minutes of inactivity
- Takes ~30 seconds to wake up
- For always-on: $7/month

---

## Option 2: Railway

### Why Railway?
- ✅ Free tier with $5 credit/month
- ✅ Very easy setup
- ✅ Auto-detects Python
- ✅ Fast deployments

### Deployment Steps:

1. **Sign up at [Railway.app](https://railway.app)**

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure:**
   - Railway auto-detects Python
   - Set root directory to `backend` in settings
   - Add environment variables in "Variables" tab

4. **Environment Variables:**
   ```
   MONGO_URI=your-mongodb-connection-string
   JWT_SECRET_KEY=your-secret-key
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

5. **Deploy:**
   - Railway automatically deploys
   - Get your URL from the service settings

---

## Option 3: Fly.io

### Why Fly.io?
- ✅ Generous free tier
- ✅ Global edge network
- ✅ Fast deployments

### Deployment Steps:

1. **Install Fly CLI:**
   ```powershell
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Create fly.toml:**
   Create `backend/fly.toml`:
   ```toml
   app = "pharmacy-backend"
   primary_region = "iad"

   [build]

   [env]
     PORT = "8080"

   [[services]]
     internal_port = 8080
     protocol = "tcp"

     [[services.ports]]
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

4. **Deploy:**
   ```bash
   cd backend
   fly launch
   fly secrets set MONGO_URI="your-connection-string"
   fly secrets set JWT_SECRET_KEY="your-secret-key"
   fly deploy
   ```

---

## Option 4: PythonAnywhere

### Why PythonAnywhere?
- ✅ Free tier available
- ✅ Simple setup
- ✅ Good for beginners

### Deployment Steps:

1. **Sign up at [PythonAnywhere.com](https://www.pythonanywhere.com)**

2. **Upload Files:**
   - Use Files tab to upload your backend files
   - Or use Git to clone repository

3. **Create Web App:**
   - Go to Web tab
   - Click "Add a new web app"
   - Choose Flask
   - Select Python 3.9 or 3.10

4. **Configure:**
   - Set source code directory
   - Set WSGI file path
   - Add environment variables

5. **Set Environment Variables:**
   - Edit WSGI file to add:
   ```python
   import os
   os.environ['MONGO_URI'] = 'your-connection-string'
   os.environ['JWT_SECRET_KEY'] = 'your-secret-key'
   ```

---

## Option 5: Heroku (Paid, but has free alternatives)

Heroku removed their free tier, but you can use:
- **Heroku Eco Dyno**: $5/month
- Or use one of the free alternatives above

---

## Quick Comparison

| Platform | Free Tier | Always On | Ease of Use | Best For |
|----------|-----------|-----------|-------------|----------|
| **Render** | ✅ Yes | ⚠️ Spins down | ⭐⭐⭐⭐⭐ | Most users |
| **Railway** | ✅ $5 credit | ✅ Yes | ⭐⭐⭐⭐⭐ | Active projects |
| **Fly.io** | ✅ Generous | ✅ Yes | ⭐⭐⭐⭐ | Global apps |
| **PythonAnywhere** | ✅ Limited | ✅ Yes | ⭐⭐⭐ | Beginners |
| **Deta Space** | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐ | When available |

---

## Recommended: Render (Easiest Alternative)

For a quick deployment when Deta Space is down, **Render** is the easiest alternative:

1. Sign up: https://render.com
2. Connect GitHub repo
3. Set root directory: `backend`
4. Add environment variables
5. Deploy!

**Your API will be at:** `https://your-app.onrender.com/api`

---

## Update Frontend After Deployment

After deploying to any platform, update your frontend:

**For local development:**
```env
# frontend/.env
VITE_API_URL=https://your-backend-url.com/api
```

**For Netlify deployment:**
- Go to Site Settings → Environment Variables
- Add: `VITE_API_URL` = `https://your-backend-url.com/api`

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Fly.io Docs**: https://fly.io/docs
- **PythonAnywhere Docs**: https://help.pythonanywhere.com

