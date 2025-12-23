# How MONGO_URI is Used in Your Code

## Current Behavior

### Code Analysis (backend/app.py):

**Line 95:**
```python
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority')
```

**How it works:**
1. ✅ Reads from environment variable `MONGO_URI`
2. ✅ Falls back to placeholder if not set
3. ✅ Also loads from `.env` file (via `load_dotenv()` on line 13)

**Line 114-115:**
```python
if not MONGO_URI or 'username:password' in MONGO_URI:
    raise ConnectionError("MONGO_URI not configured. Please set MONGO_URI environment variable.")
```

**Line 130-131:**
```python
if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
    print(f"Warning: MongoDB connection skipped in CI environment: {e}")
```

## Where MONGO_URI is Used

### 1. **Local Development** (.env file)
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority
```
- ✅ Code reads from `.env` file
- ✅ Used when running `python app.py` locally

### 2. **GitHub Actions** (GitHub Secrets)
- ❌ **Currently SKIPS** - Connection is skipped in CI environment
- ✅ **Can be used** - If you add it to workflow (see below)
- ⚠️ **Not needed** - Import tests don't require database connection

### 3. **Production** (Render/Railway)
- ✅ Uses environment variables set in platform dashboard
- ✅ Automatically available when app runs

## Current Status

### GitHub Actions Workflow:
- ❌ **Does NOT use MONGO_URI** from GitHub Secrets
- ✅ **SKIPS connection** in CI (by design)
- ✅ **Import test passes** without database

### Why It Skips:
The code is designed to:
1. Allow imports to succeed without database (for CI/testing)
2. Only connect when app actually runs
3. Skip connection errors in CI environment

## If You Want to Use GitHub Secret

### Option 1: Use in Workflow (Optional)

If you want to test database connection in CI, update workflow:

```yaml
- name: Check imports
  env:
    CI: true
    GITHUB_ACTIONS: true
    MONGO_URI: ${{ secrets.MONGO_URI }}  # Add this
  run: |
    python -c "import app; print('✅ All imports successful')"
```

**Note:** This is optional - current setup works fine without it.

### Option 2: Keep Current Setup (Recommended)

**Current setup is correct:**
- ✅ Import tests don't need database
- ✅ Connection happens when app runs (in production)
- ✅ Simpler and faster CI

## Summary

| Location | Uses MONGO_URI? | Source |
|----------|----------------|--------|
| **Local Dev** | ✅ Yes | `.env` file |
| **GitHub Actions** | ❌ Skips | Not used (by design) |
| **Render/Railway** | ✅ Yes | Platform environment variables |
| **GitHub Secrets** | ⚠️ Optional | Only if added to workflow |

## Recommendation

**Keep current setup:**
- ✅ GitHub Secrets are not needed for CI (import tests work without DB)
- ✅ Add MONGO_URI in Render/Railway dashboard for production
- ✅ Use `.env` file for local development

**GitHub Secret is useful if:**
- You want to run actual database tests in CI
- You want to verify connection string is valid
- You're doing integration testing

**For your current use case:**
- ❌ Not needed - Import tests work fine without it
- ✅ Code will use it when app runs in production (from Render/Railway env vars)

