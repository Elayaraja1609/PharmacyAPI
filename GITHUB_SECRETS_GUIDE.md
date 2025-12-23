# How to Add MONGO_URI to GitHub

Guide for adding MongoDB connection string as a GitHub Secret for CI/CD workflows.

## Why Add MONGO_URI to GitHub?

- **For CI/CD Testing**: If you want to run actual database tests in GitHub Actions
- **For Deployment**: Some deployment platforms can pull secrets from GitHub
- **Security**: Secrets are encrypted and never exposed in logs

⚠️ **Note**: For local development, use `.env` file (never commit it!)

---

## Step-by-Step: Add MONGO_URI as GitHub Secret

### Step 1: Get Your MongoDB Connection String

1. **Go to MongoDB Atlas:**
   - Visit: https://cloud.mongodb.com
   - Sign in to your account

2. **Get Connection String:**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - It looks like:
     ```
     mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/pharmacy?retryWrites=true&w=majority
     ```

3. **Replace Placeholders:**
   - Replace `<password>` with your actual database password
   - Replace `<dbname>` with `pharmacy` (or your database name)
   - Final string should be:
     ```
     mongodb+srv://myuser:mypassword@cluster0.xxxxx.mongodb.net/pharmacy?retryWrites=true&w=majority
     ```

### Step 2: Add Secret to GitHub Repository

1. **Go to Your Repository:**
   - Visit: https://github.com/Elayaraja1609/PharmacyAPI
   - Or navigate to your repository on GitHub

2. **Open Settings:**
   - Click the **"Settings"** tab (top menu)
   - You need to be a repository owner/admin to see Settings

3. **Navigate to Secrets:**
   - In the left sidebar, find **"Security"** section
   - Click **"Secrets and variables"**
   - Click **"Actions"**

4. **Add New Secret:**
   - Click **"New repository secret"** button
   - **Name**: `MONGO_URI` (exactly as shown, case-sensitive)
   - **Secret**: Paste your MongoDB connection string
   - Click **"Add secret"**

5. **Verify:**
   - You should see `MONGO_URI` in the list
   - The value will be hidden (shows dots: `••••••••`)

---

## Visual Guide

```
GitHub Repository
  └─ Settings Tab
      └─ Security (left sidebar)
          └─ Secrets and variables
              └─ Actions
                  └─ New repository secret
                      └─ Name: MONGO_URI
                      └─ Value: mongodb+srv://...
                      └─ Add secret
```

---

## Using MONGO_URI in GitHub Actions

### Option 1: Use in Workflow (If Needed)

If you want to use `MONGO_URI` in your workflow for testing, update `.github/workflows/deploy-backend.yml`:

```yaml
- name: Check imports
  working-directory: ./backend
  env:
    CI: true
    GITHUB_ACTIONS: true
    MONGO_URI: ${{ secrets.MONGO_URI }}  # Add this if you want to test with real DB
  run: |
    python -c "import app; print('✅ All imports successful')"
```

**Note**: Currently, your workflow doesn't need `MONGO_URI` because we made the connection lazy. But you can add it if you want to run actual database tests.

### Option 2: For Deployment Platforms

Some platforms (like Render, Railway) can pull secrets from GitHub, but it's usually better to add them directly in the platform's dashboard.

---

## Security Best Practices

### ✅ DO:
- ✅ Use GitHub Secrets for sensitive data
- ✅ Use strong MongoDB passwords
- ✅ Rotate secrets periodically
- ✅ Use different databases for development/production
- ✅ Limit IP access in MongoDB Atlas

### ❌ DON'T:
- ❌ Never commit `.env` files to Git
- ❌ Never hardcode secrets in code
- ❌ Never share secrets in issues/pull requests
- ❌ Never log secrets in console output

---

## Local Development Setup

For local development, use `.env` file (NOT GitHub Secrets):

1. **Create `.env` file in `backend/` directory:**
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority
   JWT_SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   FLASK_DEBUG=True
   PORT=5000
   ```

2. **Make sure `.env` is in `.gitignore`:**
   - Check that `.gitignore` includes `.env`
   - Never commit `.env` to Git

3. **Use `.env.example` as template:**
   - Copy from `backend/.env.example`
   - Fill in your actual values

---

## When Do You Need GitHub Secrets?

### ✅ You NEED GitHub Secrets if:
- You want to run database tests in CI/CD
- You're using GitHub Actions to deploy
- You want to test API endpoints with real database

### ❌ You DON'T NEED GitHub Secrets if:
- You're only testing imports (current setup)
- You're deploying to Render/Railway (add secrets there instead)
- You're only doing local development

---

## Current Setup (Recommended)

**Your current workflow doesn't require `MONGO_URI` in GitHub Secrets** because:
- ✅ MongoDB connection is lazy (only connects when app runs)
- ✅ Import test doesn't need database connection
- ✅ Deployment platforms (Render/Railway) have their own secret management

**You only need `MONGO_URI` in:**
- ✅ Local `.env` file (for development)
- ✅ Render/Railway environment variables (for deployment)

---

## Adding to Render/Railway (For Deployment)

### Render:
1. Go to your service in Render Dashboard
2. Click "Environment" tab
3. Add environment variable:
   - **Key**: `MONGO_URI`
   - **Value**: Your MongoDB connection string
4. Save and redeploy

### Railway:
1. Go to your project in Railway
2. Click "Variables" tab
3. Add variable:
   - **Key**: `MONGO_URI`
   - **Value**: Your MongoDB connection string
4. Save (auto-deploys)

---

## Troubleshooting

### "Secrets not found" Error:
- ✅ Check secret name is exactly `MONGO_URI` (case-sensitive)
- ✅ Make sure you're in the correct repository
- ✅ Verify you have admin access to the repository

### "Connection failed" Error:
- ✅ Verify MongoDB connection string is correct
- ✅ Check MongoDB Atlas IP whitelist (add `0.0.0.0/0` for all IPs)
- ✅ Verify database user password is correct
- ✅ Check network access in MongoDB Atlas

### "Permission denied" Error:
- ✅ You need to be repository owner/admin
- ✅ Check repository settings permissions

---

## Quick Reference

| Location | Purpose | How to Add |
|----------|---------|------------|
| **GitHub Secrets** | CI/CD workflows | Settings → Secrets → Actions → New secret |
| **Local `.env`** | Development | Create `.env` file in `backend/` |
| **Render** | Production deployment | Service → Environment → Add variable |
| **Railway** | Production deployment | Project → Variables → Add variable |

---

## Summary

**For your current setup:**
- ✅ **Local Development**: Use `.env` file
- ✅ **CI/CD**: No `MONGO_URI` needed (lazy connection)
- ✅ **Deployment**: Add `MONGO_URI` in Render/Railway dashboard

**If you want to add it to GitHub anyway (optional):**
1. Go to: https://github.com/Elayaraja1609/PharmacyAPI/settings/secrets/actions
2. Click "New repository secret"
3. Name: `MONGO_URI`
4. Value: Your MongoDB connection string
5. Click "Add secret"

That's it! 🎉

