# How to Get Render API Key and Service ID

Step-by-step guide to create `RENDER_API_KEY` and `RENDER_SERVICE_ID` for GitHub Actions.

---

## Prerequisites

- Render account (sign up at https://render.com if you don't have one)
- GitHub repository: `Elayaraja1609/PharmacyAPI`
- A Render service already created (or we'll create one)

---

## Step 1: Get Render API Key

### Option A: From Render Dashboard (Recommended)

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com
   - Sign in to your account

2. **Navigate to Account Settings:**
   - Click on your **profile icon** (top right corner)
   - Select **"Account Settings"** from the dropdown

3. **Go to API Keys Section:**
   - In the left sidebar, click **"API Keys"**
   - Or go directly to: https://dashboard.render.com/account/api-keys

4. **Create New API Key:**
   - Click the **"Create API Key"** button
   - Enter a name: `GitHub Actions CI/CD` (or any name you prefer)
   - Click **"Create"**

5. **Copy the API Key:**
   - ⚠️ **IMPORTANT**: The API key will be shown **ONLY ONCE**
   - Copy it immediately and save it securely
   - It will look like: `rnd_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - If you lose it, you'll need to create a new one

6. **Save the API Key:**
   - Paste it somewhere safe (password manager, notes app, etc.)
   - You'll need it in Step 3

### Option B: Using Render CLI (Alternative)

If you have Render CLI installed:

```bash
render login
render api-keys create --name "GitHub Actions"
```

---

## Step 2: Get Render Service ID

### First, Create a Service (If You Haven't)

If you don't have a Render service yet:

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com

2. **Create New Web Service:**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository: `Elayaraja1609/PharmacyAPI`
   - Configure:
     - **Name**: `pharmacy-backend`
     - **Root Directory**: `backend`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
   - Add environment variables (MONGO_URI, JWT_SECRET_KEY, etc.)
   - Click **"Create Web Service"**

3. **Wait for deployment** (optional - you can get the Service ID immediately)

### Get Service ID from Existing Service

1. **Go to Your Service:**
   - In Render Dashboard, click on your service (e.g., `pharmacy-backend`)

2. **Find Service ID in URL:**
   - Look at your browser's address bar
   - URL will be: `https://dashboard.render.com/web-services/[SERVICE_ID]`
   - The `[SERVICE_ID]` is a long string like: `srv-xxxxxxxxxxxxxxxxxxxxx`
   - **Copy this Service ID**

3. **Or Get from Service Settings:**
   - Click **"Settings"** tab in your service
   - Scroll down to find **"Service ID"**
   - Copy the Service ID

4. **Service ID Format:**
   - Looks like: `srv-xxxxxxxxxxxxxxxxxxxxx`
   - Usually starts with `srv-`

---

## Step 3: Add Secrets to GitHub

Now that you have both values, add them to GitHub:

### Step 3.1: Add RENDER_API_KEY

1. **Go to GitHub Repository:**
   - Visit: https://github.com/Elayaraja1609/PharmacyAPI

2. **Navigate to Secrets:**
   - Click **"Settings"** tab (top menu)
   - In left sidebar: **"Security"** → **"Secrets and variables"** → **"Actions"**
   - You should see: "Repository secrets" section

3. **Add RENDER_API_KEY:**
   - Click **"New repository secret"** button
   - **Name**: `RENDER_API_KEY` (exactly as shown, case-sensitive)
   - **Secret**: Paste your Render API key (from Step 1)
   - Click **"Add secret"**

### Step 3.2: Add RENDER_SERVICE_ID

1. **Still on the Secrets page:**
   - Click **"New repository secret"** button again

2. **Add RENDER_SERVICE_ID:**
   - **Name**: `RENDER_SERVICE_ID` (exactly as shown, case-sensitive)
   - **Secret**: Paste your Render Service ID (from Step 2)
   - Click **"Add secret"**

### Step 3.3: Verify Secrets Added

You should now see:
- ✅ `RENDER_API_KEY` (hidden, shows dots)
- ✅ `RENDER_SERVICE_ID` (hidden, shows dots)

---

## Step 4: Test the Setup

### Option A: Manual Trigger

1. **Go to Actions Tab:**
   - In your GitHub repo, click **"Actions"** tab

2. **Run Workflow:**
   - Select **"Deploy Backend to Production"** workflow
   - Click **"Run workflow"** button (right side)
   - Select branch: `main`
   - Click **"Run workflow"**

3. **Watch It Deploy:**
   - You'll see the workflow running
   - It will:
     1. Run tests
     2. Deploy to Render (if tests pass)
   - Check the logs to see deployment progress

### Option B: Push to Trigger

1. **Make a small change:**
   ```bash
   # Add a comment to backend/app.py
   ```

2. **Commit and push:**
   ```bash
   git add backend/app.py
   git commit -m "Test CI/CD deployment"
   git push origin main
   ```

3. **Check Actions:**
   - Go to **"Actions"** tab
   - You'll see the workflow automatically triggered
   - Watch it deploy!

---

## Visual Guide

### Render API Key Location:

```
Render Dashboard
  └─ Profile Icon (top right)
      └─ Account Settings
          └─ API Keys (left sidebar)
              └─ Create API Key
                  └─ Copy the key (shown only once!)
```

### Render Service ID Location:

```
Render Dashboard
  └─ Your Service (pharmacy-backend)
      └─ Settings Tab
          └─ Service ID (scroll down)
              └─ Copy the ID
```

### GitHub Secrets Location:

```
GitHub Repository
  └─ Settings Tab
      └─ Security (left sidebar)
          └─ Secrets and variables
              └─ Actions
                  └─ New repository secret
                      └─ Add RENDER_API_KEY
                      └─ Add RENDER_SERVICE_ID
```

---

## Troubleshooting

### "API Key Invalid" Error:

- ✅ Make sure you copied the **entire** API key
- ✅ Check for extra spaces before/after
- ✅ Verify the key starts with `rnd_`
- ✅ Create a new API key if needed

### "Service ID Not Found" Error:

- ✅ Make sure you copied the **entire** Service ID
- ✅ Verify it starts with `srv-`
- ✅ Check that the service exists in Render
- ✅ Make sure you're using the correct Render account

### Workflow Not Triggering:

- ✅ Check that secrets are added correctly
- ✅ Verify branch name is `main` or `master`
- ✅ Check workflow file exists: `.github/workflows/deploy-backend.yml`
- ✅ Make sure you pushed changes to `backend/` folder

### Deployment Fails:

- ✅ Check Render service is running
- ✅ Verify environment variables in Render are set
- ✅ Check Render logs for errors
- ✅ Verify MongoDB connection string is correct

---

## Security Best Practices

1. ✅ **Never commit secrets to Git**
   - Secrets should only be in GitHub Secrets
   - Never in code files

2. ✅ **Rotate API keys regularly**
   - Create new keys periodically
   - Delete old unused keys

3. ✅ **Use different keys for different purposes**
   - One for GitHub Actions
   - One for local development (if needed)

4. ✅ **Limit API key permissions**
   - Render API keys have full access
   - Only share with trusted services

---

## Quick Reference

### Render API Key:
- **Location**: Render Dashboard → Account Settings → API Keys
- **Format**: `rnd_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Created**: One-time display, save immediately

### Render Service ID:
- **Location**: Service Settings → Service ID
- **Format**: `srv-xxxxxxxxxxxxxxxxxxxxx`
- **Found**: In URL or Settings page

### GitHub Secrets:
- **Location**: Repo Settings → Secrets and variables → Actions
- **Names**: `RENDER_API_KEY`, `RENDER_SERVICE_ID`
- **Usage**: Automatically used by GitHub Actions workflow

---

## Next Steps

Once secrets are added:

1. ✅ **Test the workflow** (see Step 4)
2. ✅ **Push code** to trigger automatic deployment
3. ✅ **Monitor deployments** in GitHub Actions tab
4. ✅ **Check Render dashboard** for deployment status

Your CI/CD is now fully configured! 🚀

---

## Alternative: Skip GitHub Actions (Easier)

**Note**: If you're using Render's built-in auto-deploy (recommended), you don't need GitHub Actions or these secrets!

Render's auto-deploy works automatically when you:
1. Connect GitHub to Render
2. Enable auto-deploy in service settings

**You only need GitHub Actions if:**
- You want custom deployment logic
- You want to deploy to multiple platforms
- You want more control over the deployment process

**For most users, Render's built-in auto-deploy is simpler and doesn't require these secrets!**

