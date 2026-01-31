# Troubleshooting Guide - Blank Screen Issue

## Common Causes & Solutions

### 1. Missing Frontend .env File
**Symptom:** Blank screen, API calls fail to localhost:8000
**Solution:** Create `frontend/.env` with:
```
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Medical Insight Engine
VITE_DEBUG=true
```

### 2. Backend Not Running
**Check:**
- Open http://localhost:8000/api/docs
- If it shows 404, backend isn't running
**Fix:** Start backend in terminal:
```powershell
cd backend
venv\Scripts\activate.bat
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Database Connection Error
**Check:** Look at backend console for "database connection refused"
**Fix:** 
```powershell
# Start PostgreSQL (if using local)
pg_ctl -D "C:\Program Files\PostgreSQL\15\data" start

# Or check Docker container
docker ps  # Should show postgres-medical running
```

### 4. CORS Error in Browser Console
**Symptom:** "Access to XMLHttpRequest blocked by CORS policy"
**Fix:** Verify backend/.env has:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. Check Browser Console (F12)
- Look for JavaScript errors (red)
- Check Network tab - see if API calls are being made
- Verify frontend is connecting to correct API URL

### 6. Port Already in Use
**Error:** "Address already in use"
**Fix:** Kill existing process:
```powershell
# Find process on port 8000
netstat -ano | findstr :8000
# Kill it (replace PID)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn app.main:app --reload --port 8001
```

## Debug Checklist
- [ ] Frontend .env exists with VITE_API_URL
- [ ] Backend running on port 8000
- [ ] Database running and accessible
- [ ] No errors in browser console (F12)
- [ ] Network tab shows API calls being made
- [ ] CORS origins configured correctly

## Quick Reset
```powershell
# Kill all Node processes
taskkill /F /IM node.exe

# Kill all Python processes
taskkill /F /IM python.exe

# Restart both
.\dev.bat
```
