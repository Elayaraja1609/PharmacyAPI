# CI/CD Deployment Guide

Complete guide for setting up Continuous Integration and Continuous Deployment (CI/CD) for your Pharmacy API backend.

## What is CI/CD?

- **CI (Continuous Integration)**: Automatically test your code when you push to GitHub
- **CD (Continuous Deployment)**: Automatically deploy your code to production after tests pass

## Benefits

✅ **Automated Testing**: Code is tested on every push  
✅ **Automated Deployment**: No manual deployment needed  
✅ **Faster Releases**: Deploy with a single `git push`  
✅ **Error Prevention**: Catch issues before deployment  
✅ **Rollback Support**: Easy to revert to previous versions  

---

## Setup Options

### Option 1: Render (Recommended - Easiest CI/CD)

Render has built-in CI/CD - no GitHub Actions needed!

#### Steps:

1. **Connect GitHub to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Select repository: `Elayaraja1609/PharmacyAPI`

2. **Configure Auto-Deploy:**
   - **Name**: `pharmacy-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or `master`)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

3. **Environment Variables:**
   - Go to "Environment" tab
   - Add:
     ```
     MONGO_URI=your-mongodb-connection-string
     JWT_SECRET_KEY=your-secret-key
     FLASK_ENV=production
     FLASK_DEBUG=False
     PORT=5000
     ```

4. **Enable Auto-Deploy:**
   - ✅ Check "Auto-Deploy" (enabled by default)
   - Every push to `main` branch will automatically deploy!

**That's it!** Render handles CI/CD automatically.

---

### Option 2: Railway (Also Has Built-in CI/CD)

Railway also has automatic deployments!

#### Steps:

1. **Connect GitHub:**
   - Go to [Railway Dashboard](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize GitHub
   - Select: `Elayaraja1609/PharmacyAPI`

2. **Configure Service:**
   - Railway auto-detects Python
   - Set root directory: `backend`
   - Add environment variables in "Variables" tab

3. **Auto-Deploy:**
   - Railway automatically deploys on every push to `main`
   - No additional setup needed!

---

### Option 3: GitHub Actions + Manual Deploy

If you want more control, use GitHub Actions for testing and manual deployment.

#### Setup:

1. **Add Secrets to GitHub:**
   - Go to your repo: https://github.com/Elayaraja1609/PharmacyAPI
   - Settings → Secrets and variables → Actions
   - Add secrets:
     - `RENDER_API_KEY` (if using Render)
     - `RENDER_SERVICE_ID` (if using Render)
     - `RAILWAY_TOKEN` (if using Railway)

2. **The workflow file is already created:**
   - `.github/workflows/deploy-backend.yml`
   - Automatically runs tests on every push
   - Deploys when tests pass

---

## Recommended: Render (Easiest)

### Why Render for CI/CD?

✅ **Zero Configuration**: Just connect GitHub  
✅ **Automatic Deployments**: Every push = new deployment  
✅ **Preview Deployments**: Test before merging  
✅ **Rollback**: One-click revert  
✅ **Free Tier**: No cost for CI/CD features  

### Complete Render Setup:

1. **Sign up**: https://render.com

2. **Create Web Service:**
   ```
   Repository: Elayaraja1609/PharmacyAPI
   Branch: main
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```

3. **Environment Variables:**
   ```
   MONGO_URI=your-mongodb-connection-string
   JWT_SECRET_KEY=your-secret-key
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

4. **Auto-Deploy Settings:**
   - ✅ Auto-Deploy: ON
   - ✅ Pull Request Previews: ON (optional)

5. **Deploy!**
   - Click "Create Web Service"
   - Render will:
     - Clone your repo
     - Install dependencies
     - Start your app
     - Give you a URL

### How It Works:

```
You push to GitHub → Render detects change → 
Builds your app → Runs tests → Deploys → 
Your app is live!
```

**Time:** ~3-5 minutes per deployment

---

## GitHub Actions Workflow (Advanced)

If you want custom CI/CD with GitHub Actions:

### The workflow file (`.github/workflows/deploy-backend.yml`) includes:

1. **Test Job:**
   - Checks out code
   - Installs Python
   - Installs dependencies
   - Runs linting
   - Verifies imports

2. **Deploy Jobs:**
   - Deploys to Render (if configured)
   - Deploys to Railway (if configured)

### To Use GitHub Actions:

1. **Get Render API Key:**
   - Go to Render Dashboard → Account Settings → API Keys
   - Create new API key
   - Copy the key

2. **Get Render Service ID:**
   - Go to your service in Render
   - Service ID is in the URL or settings

3. **Add GitHub Secrets:**
   - Repo → Settings → Secrets and variables → Actions
   - Add:
     - `RENDER_API_KEY`: Your Render API key
     - `RENDER_SERVICE_ID`: Your Render service ID

   📖 **Detailed step-by-step guide**: See `RENDER_SECRETS_SETUP.md` for complete instructions with screenshots and troubleshooting.

4. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add CI/CD workflow"
   git push origin main
   ```

5. **Watch the Magic:**
   - Go to Actions tab in GitHub
   - See your workflow run
   - Automatic deployment!

---

## Deployment Flow

### Current Flow (Manual):
```
1. Make changes
2. Test locally
3. Commit and push
4. Manually deploy to platform
5. Test production
```

### CI/CD Flow (Automatic):
```
1. Make changes
2. Commit and push to GitHub
3. ✅ GitHub Actions runs tests
4. ✅ Tests pass → Auto-deploy to Render/Railway
5. ✅ Your app is live automatically!
```

---

## Testing Before Deployment

The CI/CD workflow includes:

1. **Import Check**: Verifies all Python imports work
2. **Linting**: Checks code quality (optional)
3. **Dependency Check**: Ensures requirements.txt is valid

### Add More Tests (Optional):

Create `backend/test_app.py`:
```python
import unittest
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_root_endpoint(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_products_endpoint(self):
        response = self.app.get('/api/products')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

Add to workflow:
```yaml
- name: Run tests
  working-directory: ./backend
  run: python -m pytest test_app.py
```

---

## Branch Strategy

### Recommended:

- **main/master**: Production (auto-deploys)
- **develop**: Development (optional, for testing)
- **feature/***: Feature branches (no auto-deploy)

### Configure Branch Protection:

1. Go to GitHub repo → Settings → Branches
2. Add rule for `main`:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date

---

## Monitoring Deployments

### Render:
- Dashboard shows deployment status
- View logs in real-time
- Get notified of failures

### Railway:
- Deployments tab shows history
- View logs for each deployment
- Rollback with one click

### GitHub Actions:
- Actions tab shows all runs
- Green checkmark = success
- Red X = failure (with details)

---

## Rollback Strategy

### Render:
1. Go to Deployments tab
2. Find previous successful deployment
3. Click "Rollback"
4. Done!

### Railway:
1. Go to Deployments
2. Click on previous deployment
3. Click "Redeploy"
4. Done!

---

## Best Practices

1. ✅ **Test Locally First**: Always test before pushing
2. ✅ **Use Feature Branches**: Don't push directly to main
3. ✅ **Review Code**: Use pull requests
4. ✅ **Monitor Deployments**: Check logs after deployment
5. ✅ **Environment Variables**: Never commit secrets
6. ✅ **Version Control**: Tag releases for easy rollback

---

## Troubleshooting

### Deployment Fails:

1. **Check Logs:**
   - Render: Dashboard → Logs
   - Railway: Deployments → View logs
   - GitHub Actions: Actions tab → Failed workflow

2. **Common Issues:**
   - Missing environment variables
   - MongoDB connection error
   - Import errors
   - Port conflicts

3. **Fix and Redeploy:**
   - Fix the issue
   - Push to GitHub
   - Auto-deploy will retry

### Tests Fail:

- Check the error message in GitHub Actions
- Fix the code
- Push again
- Deployment won't happen until tests pass

---

## Quick Start: Render CI/CD (Recommended)

**Fastest way to get CI/CD working:**

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Render:**
   - Go to render.com
   - New Web Service
   - Connect GitHub repo: `Elayaraja1609/PharmacyAPI`
   - Configure (see above)
   - Deploy!

3. **That's it!** Every push = automatic deployment

---

## Next Steps

1. ✅ Set up Render account
2. ✅ Connect GitHub repository
3. ✅ Configure environment variables
4. ✅ Enable auto-deploy
5. ✅ Push code and watch it deploy!

Your CI/CD is now active! 🚀

