# Render CI/CD Quick Start Guide

**Fastest way to set up automatic deployments for your Pharmacy API!**

## Step 1: Push Your Code to GitHub

Make sure your code is pushed to: `https://github.com/Elayaraja1609/PharmacyAPI`

```bash
# If not already pushed:
cd D:\Project\Pharmecy
git add .
git commit -m "Add backend code"
git push origin main
```

## Step 2: Sign Up for Render

1. Go to: https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended - easier connection)

## Step 3: Create Web Service

1. **Click "New +"** → **"Web Service"**

2. **Connect Repository:**
   - Click "Connect account" (if not connected)
   - Authorize Render to access GitHub
   - Select repository: **`Elayaraja1609/PharmacyAPI`**
   - Click "Connect"

3. **Configure Service:**
   ```
   Name: pharmacy-backend
   Region: Choose closest to you (e.g., Singapore, US East)
   Branch: main (or master)
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```

4. **Environment Variables:**
   Click "Advanced" → "Add Environment Variable"
   
   Add these:
   ```
   MONGO_URI=your-mongodb-atlas-connection-string
   JWT_SECRET_KEY=your-secret-key-here-make-it-long-and-random
   FLASK_ENV=production
   FLASK_DEBUG=False
   PORT=5000
   ```

5. **Auto-Deploy Settings:**
   - ✅ **Auto-Deploy**: ON (default)
   - This means every push to `main` = automatic deployment!

6. **Click "Create Web Service"**

## Step 4: Wait for First Deployment

- Render will:
  1. Clone your repository
  2. Install dependencies (`pip install -r requirements.txt`)
  3. Start your app (`python app.py`)
  4. Give you a URL like: `https://pharmacy-backend.onrender.com`

**Time:** ~3-5 minutes

## Step 5: Test Your Deployment

1. **Check your API:**
   ```
   https://your-service-name.onrender.com/
   ```

2. **Check Swagger docs:**
   ```
   https://your-service-name.onrender.com/api-docs
   ```

3. **Test an endpoint:**
   ```
   https://your-service-name.onrender.com/api/products
   ```

## Step 6: Test CI/CD (Automatic Deployment)

1. **Make a small change:**
   ```bash
   # Edit backend/app.py - add a comment or small change
   ```

2. **Commit and push:**
   ```bash
   git add backend/app.py
   git commit -m "Test CI/CD deployment"
   git push origin main
   ```

3. **Watch Render Dashboard:**
   - Go to your service in Render
   - You'll see a new deployment starting automatically!
   - Wait ~3-5 minutes
   - Your changes are live! 🎉

## How It Works

```
You push to GitHub
    ↓
Render detects the change
    ↓
Builds your app (installs dependencies)
    ↓
Starts your app
    ↓
Your app is live!
```

**Every push to `main` branch = automatic deployment!**

## Viewing Logs

1. Go to your service in Render
2. Click "Logs" tab
3. See real-time logs from your Flask app

## Updating Environment Variables

1. Go to your service
2. Click "Environment" tab
3. Add/Edit variables
4. Click "Save Changes"
5. Service will automatically restart

## Rollback (If Something Breaks)

1. Go to "Deployments" tab
2. Find previous successful deployment
3. Click "Rollback"
4. Done! Your app is back to previous version

## Troubleshooting

### Deployment Fails:

1. **Check Logs:**
   - Go to "Logs" tab
   - Look for error messages
   - Common issues:
     - Missing environment variables
     - MongoDB connection error
     - Import errors

2. **Fix and Push:**
   - Fix the issue locally
   - Push to GitHub
   - Render will auto-deploy again

### App Not Starting:

- Check `Start Command`: Should be `python app.py`
- Check `Root Directory`: Should be `backend`
- Check environment variables are set correctly

### MongoDB Connection Error:

- Verify `MONGO_URI` is correct
- Check MongoDB Atlas allows connections from anywhere (0.0.0.0/0)
- Test connection string locally first

## Next Steps

1. ✅ Your backend is now live on Render
2. ✅ Every push = automatic deployment
3. ✅ Update frontend `.env` with your Render URL:
   ```
   VITE_API_URL=https://your-service-name.onrender.com/api
   ```
4. ✅ Deploy frontend to Netlify (see `DEPLOYMENT.md`)

## Pro Tips

- **Preview Deployments**: Enable "Pull Request Previews" to test before merging
- **Health Checks**: Render automatically checks if your app is running
- **Custom Domain**: Add your own domain in "Settings" → "Custom Domain"
- **Monitoring**: View metrics in "Metrics" tab

## That's It!

Your CI/CD is now active! Every time you push to GitHub, your backend will automatically deploy to Render. 🚀

**No more manual deployments needed!**

