# Deta Space Quick Start Guide

## Prerequisites Checklist

- [ ] Deta Space account created at https://deta.space
- [ ] MongoDB Atlas connection string ready
- [ ] JWT secret key generated

## Quick Deployment Steps

### 1. Install Deta Space CLI

**Windows (PowerShell):**
```powershell
# Download from: https://deta.space/docs/en/cli
# Or use winget:
winget install Deta.SpaceCLI
```

**macOS/Linux:**
```bash
curl -fsSL https://get.deta.dev/space-cli.sh | sh
```

### 2. Login
```bash
space login
```

### 3. Navigate to Backend
```bash
cd backend
```

### 4. Initialize Project
```bash
space new
```
- Enter a name for your app (e.g., `pharmacy-backend`)

### 5. Set Environment Variables
```bash
space env set MONGO_URI "mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority"
space env set JWT_SECRET_KEY "your-generated-secret-key-here"
```

**Generate JWT Secret Key:**
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Deploy
```bash
space push
```

### 7. Get Your URL
After deployment, you'll see:
```
✅ Deployed to: https://your-app-name.deta.app
```

## Update Frontend

Update `frontend/.env`:
```env
VITE_API_URL=https://your-app-name.deta.app/api
```

## Verify Deployment

1. Visit: `https://your-app-name.deta.app/api-docs` (Swagger UI)
2. Test: `https://your-app-name.deta.app/api/products`
3. Login: `https://your-app-name.deta.app/api/admin/login`

## Common Commands

```bash
# View logs
space logs

# View environment variables
space env

# Update deployment
space push

# View app info
space info
```

## Troubleshooting

**Deployment fails?**
- Check `space logs` for errors
- Verify all dependencies in `requirements.txt`
- Check `Spacefile` syntax

**MongoDB connection error?**
- Whitelist IP `0.0.0.0/0` in MongoDB Atlas
- Verify `MONGO_URI` is set correctly

**Module not found?**
- Ensure all packages in `requirements.txt`
- Check Python version in `Spacefile` (python3.9)

