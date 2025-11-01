# 🔧 ASL Summarizer - Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Issue 1: Blank White Page in Frontend

**Symptoms:**
- Frontend loads but shows only a blank white page
- No content visible in browser
- Console may show authentication or routing errors

**Root Cause:**
The frontend has authentication protection that was preventing access to the application.

**✅ SOLUTION - APPLIED:**
I've implemented a development mode bypass that automatically logs in users during development:

1. **Modified ProtectedRoute component** to skip authentication in development mode
2. **Updated AuthContext** to auto-login with mock user in development
3. **Added console logging** for debugging

**Files Modified:**
- `asl-summarizer-frontend/src/components/auth/ProtectedRoute/ProtectedRoute.jsx`
- `asl-summarizer-frontend/src/context/AuthContext.jsx`

### Issue 2: Database Connection Issues

**Symptoms:**
- Backend fails to start
- Database connection errors in logs
- Health check endpoints return database errors

**Solutions:**

1. **Initialize Database:**
   ```bash
   cd /path/to/project
   python database_handler/scripts/init_db.py
   ```

2. **Check PostgreSQL Status:**
   ```bash
   # Ubuntu/Debian
   sudo systemctl status postgresql
   
   # macOS
   brew services list | grep postgresql
   
   # Windows
   # Check Services panel for PostgreSQL service
   ```

3. **Verify Database Configuration:**
   Check `backend/.env` file:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=asl_summarizer
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

4. **Test Database Connection:**
   ```bash
   psql -h localhost -p 5432 -U postgres -d asl_summarizer
   ```

### Issue 3: Missing Dependencies

**Frontend Dependencies:**
```bash
cd asl-summarizer-frontend
npm install
```

**Backend Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue 4: CORS Issues

**Symptoms:**
- Frontend can't connect to backend
- CORS errors in browser console
- API requests fail

**Solution:**
Verify CORS configuration in `backend/.env`:
```env
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Issue 5: API Key Configuration

**Symptoms:**
- Claude API errors
- Content validation fails
- Summary generation fails

**Solution:**
Add your Anthropic API key to `backend/.env`:
```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

## 🚀 Quick Start Commands

### 1. Start Backend Server
```bash
cd backend
python run.py
```

**Expected Output:**
```
Starting ASL Summarizer Backend Server...
Host: 0.0.0.0
Port: 5000
Debug: True
Environment: development
==================================================
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
```

### 2. Start Frontend Server
```bash
cd asl-summarizer-frontend
npm run dev
```

**Expected Output:**
```
VITE v4.2.0  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 3. Test Integration
```bash
# Test backend health
curl http://localhost:5000/health/

# Expected response:
{
  "status": "healthy",
  "services": {
    "database": "up",
    "claude_api": "configured",
    "flask": "up"
  }
}
```

## 🔍 Debugging Steps

### 1. Check Browser Console
1. Open browser developer tools (F12)
2. Go to Console tab
3. Look for JavaScript errors
4. Check Network tab for failed API requests

### 2. Check Backend Logs
Backend logs will show in the terminal where you ran `python run.py`. Look for:
- Database connection errors
- API key issues
- Import errors

### 3. Verify File Structure
Ensure all files exist:
```
project/
├── asl-summarizer-frontend/
│   ├── src/
│   ├── package.json
│   └── index.html
├── backend/
│   ├── app/
│   ├── run.py
│   └── .env
└── database_handler/
    ├── __init__.py
    └── scripts/
```

### 4. Test Individual Components

**Test Database Handler:**
```bash
cd /path/to/project
python -c "
from database_handler import DatabaseHandler, DatabaseConfig
from database_handler.config import load_config_from_env
config = load_config_from_env()
with DatabaseHandler(config) as db:
    db.initialize()
    print('Database connection successful!')
"
```

**Test Backend API:**
```bash
# Test health endpoint
curl http://localhost:5000/health/

# Test sources endpoint
curl http://localhost:5000/api/sources
```

## 🎯 Development Mode Features

### Authentication Bypass
- **Automatic login** in development mode
- **Mock user** created automatically
- **No login required** for testing

### Debug Information
- **Console logging** for authentication flow
- **Detailed error messages** in development
- **Network request logging** in browser

### Hot Reload
- **Frontend**: Automatic reload on file changes
- **Backend**: Manual restart required for code changes

## 🔧 Configuration Files

### Frontend Environment (.env)
```env
# Optional - defaults work for most setups
REACT_APP_API_URL=http://localhost:5000/api
```

### Backend Environment (.env)
```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# REQUIRED: Add your Claude API key
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=asl_summarizer
DB_USER=postgres
DB_PASSWORD=your_password

# CORS Configuration
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🧪 Testing the Application

### 1. Access Frontend
- Open http://localhost:5173
- Should see ASL Summarizer homepage
- No login required in development mode

### 2. Test Navigation
- Click "Sources" - should load sources page
- Click "Summaries" - should load summaries page
- All navigation should work without errors

### 3. Test Backend Integration
- Sources page should load data from backend
- Upload functionality should work
- Summary generation should work (with valid API key)

## 📞 Getting Help

### Check Logs
1. **Frontend**: Browser console (F12)
2. **Backend**: Terminal output
3. **Database**: PostgreSQL logs

### Common Error Messages

**"Module not found"**
- Run `npm install` or `pip install -r requirements.txt`

**"Database connection failed"**
- Check PostgreSQL is running
- Verify database credentials
- Run database initialization script

**"CORS error"**
- Check CORS_ORIGINS in backend .env
- Ensure frontend URL matches

**"API key error"**
- Add valid ANTHROPIC_API_KEY to backend .env
- Check API key format and permissions

## ✅ Success Indicators

Your setup is working correctly when:

- ✅ Frontend loads at http://localhost:5173
- ✅ Backend responds at http://localhost:5000/health/
- ✅ Homepage shows navigation cards
- ✅ Sources page loads without errors
- ✅ No console errors in browser
- ✅ Database connection successful
- ✅ API endpoints respond correctly

---

**🎉 With these fixes applied, your ASL Summarizer should now work correctly!**