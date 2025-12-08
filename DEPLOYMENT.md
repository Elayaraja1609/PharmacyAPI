# Deployment Guide

This guide will help you deploy the Local Pharmacy application to production.

## Prerequisites

- MongoDB Atlas account (free tier available)
- Netlify account (for frontend)
- Render or Railway account (for backend)
- Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create a free account
2. Create a new cluster (choose the free M0 tier)
3. Create a database user:
   - Go to Database Access
   - Add New Database User
   - Choose Password authentication
   - Save the username and password
4. Whitelist IP addresses:
   - Go to Network Access
   - Add IP Address
   - For development: Add your current IP
   - For production: Add `0.0.0.0/0` (allows all IPs) or your server's IP
5. Get your connection string:
   - Go to Database → Connect
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password
   - Replace `<dbname>` with `pharmacy` (or your preferred database name)

## Step 2: Backend Deployment

### Option A: Deploy to Render

1. **Prepare your repository:**
   - Push your code to GitHub/GitLab/Bitbucket
   - Ensure `backend/requirements.txt` is committed

2. **Create a new Web Service on Render:**
   - Sign up/login at [Render](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your repository
   - Select the repository and branch

3. **Configure the service:**
   - **Name**: `pharmacy-backend` (or your choice)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

4. **Add Environment Variables:**
   - Click "Environment" tab
   - Add the following variables:
     ```
     MONGO_URI=your-mongodb-connection-string
     JWT_SECRET_KEY=generate-a-random-secret-key-here
     FLASK_ENV=production
     FLASK_DEBUG=False
     PORT=5000
     ```
   - Generate a strong JWT secret key (you can use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

5. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy your application
   - Note the service URL (e.g., `https://pharmacy-backend.onrender.com`)

### Option B: Deploy to Railway

1. **Sign up/login to Railway:**
   - Go to [Railway](https://railway.app)
   - Sign up with GitHub

2. **Create a new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure the service:**
   - Railway will auto-detect Python
   - Set the root directory to `backend` in settings
   - Add a `Procfile` in the backend directory:
     ```
     web: python app.py
     ```

4. **Add Environment Variables:**
   - Go to Variables tab
   - Add:
     ```
     MONGO_URI=your-mongodb-connection-string
     JWT_SECRET_KEY=your-secret-key
     FLASK_ENV=production
     FLASK_DEBUG=False
     ```

5. **Deploy:**
   - Railway will automatically deploy
   - Get your service URL from the settings

## Step 3: Frontend Deployment (Netlify)

1. **Build the frontend locally (optional test):**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Update environment variables:**
   - Create `frontend/.env.production`:
     ```
     VITE_API_URL=https://your-backend-url.com/api
     ```
   - Update `frontend/public/sitemap.xml` with your domain
   - Update `frontend/public/robots.txt` with your domain

3. **Deploy to Netlify:**

   **Option A: Drag and Drop**
   - Go to [Netlify](https://www.netlify.com)
   - Sign up/login
   - Drag the `frontend/dist` folder to Netlify dashboard
   - Add environment variable:
     - Go to Site settings → Environment variables
     - Add `VITE_API_URL` = `https://your-backend-url.com/api`

   **Option B: Git Integration (Recommended)**
   - Connect your Git repository
   - Set build settings:
     - **Base directory**: `frontend`
     - **Build command**: `npm run build`
     - **Publish directory**: `frontend/dist`
   - Add environment variable:
     - `VITE_API_URL` = `https://your-backend-url.com/api`
   - Deploy

4. **Update CORS in Backend (if needed):**
   - If you get CORS errors, update `backend/app.py`:
     ```python
     CORS(app, origins=["https://your-netlify-domain.netlify.app"])
     ```

## Step 4: Post-Deployment Checklist

- [ ] Backend is accessible and returning responses
- [ ] Frontend can connect to backend API
- [ ] Admin login works
- [ ] Products can be added/viewed
- [ ] Orders can be created
- [ ] MongoDB connection is working
- [ ] Environment variables are set correctly
- [ ] CORS is configured properly
- [ ] SSL/HTTPS is enabled (automatic on Netlify/Render/Railway)

## Step 5: Update SEO Files

1. **Update sitemap.xml:**
   - Replace `https://your-domain.com` with your actual Netlify domain
   - Update `lastmod` dates

2. **Update robots.txt:**
   - Replace `https://your-domain.com` with your actual domain

## Troubleshooting

### Backend Issues

**Issue: MongoDB connection error**
- Check MongoDB Atlas IP whitelist includes your server IP
- Verify connection string is correct
- Check database user has proper permissions

**Issue: CORS errors**
- Update CORS configuration in `app.py`
- Ensure frontend URL is whitelisted

**Issue: JWT errors**
- Verify `JWT_SECRET_KEY` is set
- Check token expiration settings

### Frontend Issues

**Issue: API calls failing**
- Verify `VITE_API_URL` environment variable is set
- Check backend URL is correct
- Verify CORS is configured

**Issue: Build fails**
- Check Node.js version (should be 16+)
- Clear `node_modules` and reinstall
- Check for TypeScript/ESLint errors

## Custom Domain Setup

### Netlify Custom Domain
1. Go to Site settings → Domain management
2. Add custom domain
3. Follow DNS configuration instructions
4. Update `sitemap.xml` and `robots.txt` with new domain

### Backend Custom Domain (Render/Railway)
- Both platforms support custom domains
- Configure in your service settings
- Update frontend `VITE_API_URL` accordingly

## Monitoring and Maintenance

1. **Monitor logs:**
   - Render: Dashboard → Logs
   - Railway: Deployments → View logs
   - Netlify: Deploy logs

2. **Set up error tracking:**
   - Consider adding Sentry or similar service

3. **Database backups:**
   - MongoDB Atlas provides automatic backups on paid tiers
   - Consider manual backups for free tier

4. **Performance:**
   - Monitor API response times
   - Optimize database queries if needed
   - Use CDN for static assets (Netlify provides this)

## Security Checklist

- [ ] Strong JWT secret key (32+ characters, random)
- [ ] MongoDB user has minimal required permissions
- [ ] IP whitelist configured in MongoDB Atlas
- [ ] Environment variables not committed to Git
- [ ] HTTPS enabled (automatic on these platforms)
- [ ] Admin password changed from default
- [ ] CORS configured to only allow your frontend domain

## Cost Estimation

**Free Tier:**
- MongoDB Atlas: Free (M0 cluster)
- Netlify: Free (100GB bandwidth/month)
- Render: Free (spins down after 15 min inactivity)
- Railway: Free tier available (limited hours/month)

**Paid Options (if needed):**
- Render: $7/month for always-on service
- Railway: Pay-as-you-go
- MongoDB Atlas: Starts at $9/month for M10 cluster

## Support

For platform-specific issues:
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Netlify Docs](https://docs.netlify.com)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com)

