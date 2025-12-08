# Deploying to Deta Space - Complete Guide

⚠️ **Note**: If you're experiencing DNS errors with Deta Space, see the "Alternative Deployment Options" section below or check [Deta Space Status](https://status.deta.space).

This guide will help you deploy your Flask pharmacy backend to Deta Space, which provides a free domain and hosting.

## Prerequisites

1. **Deta Space Account**: Sign up at [https://deta.space](https://deta.space)
2. **Space CLI**: Install the Deta Space CLI
3. **MongoDB Atlas**: Your MongoDB connection string
4. **Git** (optional, but recommended)

## Step 1: Install Deta Space CLI

### Windows:
1. Download the installer from [Deta Space CLI](https://deta.space/docs/en/cli)
2. Run the installer
3. Or use PowerShell:
   ```powershell
   # Using Scoop (if installed)
   scoop install deta-space
   
   # Or download from: https://deta.space/docs/en/cli
   ```

### macOS/Linux:
```bash
curl -fsSL https://get.deta.dev/space-cli.sh | sh
```

### Verify Installation:
```bash
space version
```

## Step 2: Login to Deta Space

```bash
space login
```

This will open your browser for authentication. Complete the login process.

## Step 3: Prepare Your Backend

### 3.1. Update Environment Variables

Create a `.env` file in the `backend` directory (if you haven't already):
```env
MONGO_URI=your-mongodb-atlas-connection-string
JWT_SECRET_KEY=your-strong-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
```

**Important**: Generate a strong JWT secret key:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3.2. Verify Spacefile

The `Spacefile` is already created in your backend directory. It should look like:
```yaml
v: 0
app_name: pharmacy-backend
micros:
  - name: api
    src: ./
    engine: python3.9
    run: python app.py
    env:
      - key: MONGO_URI
        value: ${{MONGO_URI}}
      - key: JWT_SECRET_KEY
        value: ${{JWT_SECRET_KEY}}
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: "False"
```

## Step 4: Initialize Deta Space Project

Navigate to your backend directory:
```bash
cd backend
```

Initialize a new Deta Space project:
```bash
space new
```

This will:
- Create a `.space` directory (hidden)
- Set up the project structure
- You may be asked to name your app

## Step 5: Set Environment Variables in Deta Space

Before deploying, set your environment variables in Deta Space:

### Option A: Using Space CLI
```bash
space env set MONGO_URI "your-mongodb-connection-string"
space env set JWT_SECRET_KEY "your-secret-key"
```

### Option B: Using Deta Space Dashboard
1. Go to [Deta Space Dashboard](https://deta.space/discover)
2. Find your app
3. Go to Settings → Environment Variables
4. Add:
   - `MONGO_URI`: Your MongoDB Atlas connection string
   - `JWT_SECRET_KEY`: Your JWT secret key
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`

## Step 6: Deploy to Deta Space

Deploy your application:
```bash
space push
```

This will:
- Upload your code to Deta Space
- Install dependencies from `requirements.txt`
- Start your Flask application
- Provide you with a deployment URL

## Step 7: Access Your Deployed App

After successful deployment, you'll get a URL like:
```
https://your-app-name.deta.app
```

Your API will be available at:
- API Base: `https://your-app-name.deta.app/api`
- Swagger UI: `https://your-app-name.deta.app/api-docs`
- Root: `https://your-app-name.deta.app/`

## Step 8: Update Frontend API URL

Update your frontend `.env` file (or environment variables in Netlify):
```env
VITE_API_URL=https://your-app-name.deta.app/api
```

## Troubleshooting

### Issue: Deployment fails
- Check that all dependencies are in `requirements.txt`
- Verify your `Spacefile` syntax is correct
- Check logs: `space logs`

### Issue: Module not found errors
- Ensure all packages are in `requirements.txt`
- Check that the Python version in Spacefile matches your local version

### Issue: MongoDB connection errors
- Verify `MONGO_URI` is set correctly in Deta Space
- Check MongoDB Atlas IP whitelist includes Deta Space IPs (or use 0.0.0.0/0)
- Ensure your MongoDB user has proper permissions

### Issue: CORS errors
- The backend already has CORS enabled
- If issues persist, update CORS in `app.py`:
  ```python
  CORS(app, origins=["https://your-frontend-domain.netlify.app"])
  ```

### View Logs
```bash
space logs
```

### Update Deployment
After making changes:
```bash
space push
```

## Deta Space Features

- **Free Domain**: Get a free `.deta.app` domain
- **HTTPS**: Automatic SSL certificates
- **Auto-scaling**: Handles traffic automatically
- **Environment Variables**: Secure variable storage
- **Logs**: View application logs
- **Free Tier**: Generous free tier for small applications

## Important Notes

1. **MongoDB Atlas**: Make sure to whitelist Deta Space IPs or allow all IPs (0.0.0.0/0) in MongoDB Atlas Network Access

2. **JWT Secret**: Use a strong, random secret key in production

3. **Debug Mode**: Always set `FLASK_DEBUG=False` in production

4. **Port**: The app automatically uses the PORT environment variable provided by Deta Space

5. **File Size Limits**: Deta Space has file size limits, ensure your uploads are reasonable

## Alternative: Using Deta Space Dashboard

You can also deploy via the web dashboard:
1. Go to [Deta Space Dashboard](https://deta.space/discover)
2. Click "New" → "Micro"
3. Connect your Git repository OR upload files
4. Configure environment variables
5. Deploy

## Next Steps

1. ✅ Deploy backend to Deta Space
2. ✅ Update frontend API URL
3. ✅ Test all endpoints
4. ✅ Update Swagger documentation URLs if needed
5. ✅ Test admin login
6. ✅ Add sample data

## Troubleshooting DNS Errors

If you see "Error 1016: Origin DNS error" when accessing deta.space:

1. **Check Deta Space Status**: Visit [Deta Space Status Page](https://status.deta.space) or their Twitter
2. **Wait and Retry**: DNS issues are usually temporary
3. **Use Alternative**: See `ALTERNATIVE_DEPLOYMENT.md` for other free hosting options
4. **Try Later**: DNS propagation can take time

## Alternative Deployment Options

If Deta Space is unavailable, see `ALTERNATIVE_DEPLOYMENT.md` for:
- Render (Recommended - Easy setup)
- Railway (Fast deployment)
- Fly.io (Global edge network)
- PythonAnywhere (Beginner-friendly)

## Support

- [Deta Space Documentation](https://deta.space/docs)
- [Deta Space Community](https://deta.space/community)
- [Space CLI Docs](https://deta.space/docs/en/cli)
- [Deta Space Status](https://status.deta.space)

