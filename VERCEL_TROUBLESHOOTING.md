# Vercel Serverless Troubleshooting Guide

## Common Serverless Crash Issues & Fixes

### 1. **Module-Level Initialization Failure** ✅ FIXED
**Problem:** CoreBrain, GoalManager, etc. initialized at import time
**Solution:** Implemented lazy initialization - engines load only when first endpoint is called

### 2. **Import Path Issues** ✅ FIXED
**Problem:** Relative imports fail in serverless environment
**Solution:** Added project root to sys.path in `api/index.py`

### 3. **Fallback Error Handling** ✅ FIXED
**Problem:** Any import error causes complete serverless crash
**Solution:** Created minimal FastAPI app in `api/index.py` if main import fails

### 4. **Frontend Static Files** ✅ FIXED
**Problem:** Frontend paths don't exist in serverless, causing crashes
**Solution:** Wrapped in try-except, mounted to `/static` instead of root

### 5. **API Router Dependencies** ✅ FIXED
**Problem:** API router import could fail silently
**Solution:** Wrapped router loading in try-except with warning logs

## Files Modified

1. **vercel.json** - Correct function entry point to `api/index.py`
2. **api/index.py** - Robust entry point with error fallback
3. **src/aether/main.py** - Error handling for router and static files
4. **.vercelignore** - Exclude unnecessary files from deployment

## How to View Logs

### Option 1: Vercel Web Dashboard
1. Go to https://vercel.com
2. Select your project "studymentor"
3. Go to **Deployments** → Click latest deployment
4. Click **Functions** tab to see function logs
5. Click on `api/index` to see runtime logs

### Option 2: Vercel CLI
```powershell
# Authenticate first
npx vercel login

# View logs (replace with your project name)
npx vercel logs studymentor --follow
```

### Option 3: Check Build Logs
```powershell
npx vercel logs studymentor --builds
```

## Debugging Steps

1. **Check if app starts locally:**
   ```powershell
   python -m uvicorn src.aether.main:app --reload
   ```

2. **Test import chain:**
   ```powershell
   python -c "from src.aether.main import app; print('Import successful')"
   ```

3. **Check for missing dependencies:**
   ```powershell
   pip list | findstr "fastapi uvicorn pydantic google"
   ```

## Environment Variables

Make sure these are set in Vercel dashboard:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `LLM_PROVIDER` - Set to "gemini"

Settings → Environment Variables

## Health Check Endpoint

After deployment, test with:
```
GET https://your-vercel-url.vercel.app/health
```

Should return:
```json
{
  "status": "healthy",
  "system": "AETHER 2.0",
  "version": "2.0.0"
}
```

## Common Errors & Solutions

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'src'` | Import path issue | Check `api/index.py` sys.path |
| `AttributeError: 'NoneType' has no attribute` | Engine initialization failed | Check if get_*() returns None |
| `FileNotFoundError: frontend directory` | Static files path wrong | Already fixed in main.py |
| `Internal Server Error (500)` | Missing dependencies | Run `pip install -r requirements.txt` |

## Next Steps

1. Commit and push these changes
2. Vercel will auto-deploy
3. Check Vercel dashboard for logs
4. Share screenshot of error if still crashing
