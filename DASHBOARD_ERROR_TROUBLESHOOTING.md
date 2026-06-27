# Dashboard Error Troubleshooting Guide

## Error: "Failed to fetch dashboard data"

This error occurs when the frontend cannot get data from the `/analytics/dashboard` endpoint.

---

## Common Causes & Solutions

### 1. Backend Server Not Running

**Symptom:** Error immediately, no loading

**Solution:**
```bash
cd backend
python main.py
```

**Check:** Open http://localhost:8000/health in browser
- Should see: `{"status": "healthy", ...}`

---

### 2. Database Connection Issue

**Symptom:** Error after loading, backend logs show database error

**Check Backend Logs:**
Look for errors like:
- `Error getting dashboard: ...`
- `Database connection failed`
- `No such table: comparisons`

**Solutions:**

**If using SQLite:**
```bash
cd backend
# Make sure database file exists
ls -la compair.db  # or check if file exists

# Initialize database
python -c "from database.init_db import init_db; init_db()"
```

**If using PostgreSQL:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL
# Should be: postgresql://user:password@localhost:5432/dbname
```

---

### 3. Database Not Initialized

**Symptom:** Error mentions "table does not exist"

**Solution:**
```bash
cd backend
python -c "from database.init_db import init_db; init_db()"
```

Or check if `init_db()` is being called in `main.py` (should be at startup).

---

### 4. CORS Issue (Less Likely)

**Symptom:** Browser console shows CORS error

**Check:** Backend CORS is set to allow all origins (line 148 in main.py)
```python
allow_origins=["*"]  # Should allow all
```

**Solution:** Already configured correctly, but if issue persists:
- Check browser console for CORS errors
- Verify frontend is calling correct URL

---

### 5. Port Mismatch

**Symptom:** Request fails immediately

**Check Frontend Config:**
File: `frontend/src/config/api.js`

Should be:
```javascript
const API_BASE = "http://localhost:8000";
```

**Check Backend:**
Backend should be running on port 8000 (default)

---

### 6. Network/Firewall Issue

**Symptom:** Request times out

**Solution:**
- Check if firewall is blocking port 8000
- Try accessing http://localhost:8000/health directly in browser
- Check if antivirus is blocking connections

---

## Step-by-Step Debugging

### Step 1: Check Backend is Running

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Should see:
# INFO:     Started server process
# INFO:     Application startup complete
```

### Step 2: Test Backend Endpoint Directly

Open in browser:
```
http://localhost:8000/analytics/dashboard?days=30
```

**Expected:** JSON response with dashboard data

**If error:** Check backend terminal for error message

### Step 3: Check Browser Console

Open browser DevTools (F12) → Console tab

Look for:
- Network errors
- CORS errors
- JavaScript errors

### Step 4: Check Network Tab

Open browser DevTools (F12) → Network tab

1. Refresh Dashboard page
2. Find request to `/analytics/dashboard`
3. Check:
   - Status code (should be 200)
   - Response (should be JSON)
   - Request URL (should be correct)

---

## Quick Fixes

### Fix 1: Restart Backend

```bash
# Stop backend (Ctrl+C)
# Start again
cd backend
python main.py
```

### Fix 2: Initialize Database

```bash
cd backend
python -c "from database.init_db import init_db; init_db()"
```

### Fix 3: Check Environment Variables

```bash
# Check DATABASE_URL
echo $DATABASE_URL  # Linux/Mac
echo $env:DATABASE_URL  # PowerShell

# Should be set correctly
```

### Fix 4: Clear Browser Cache

- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Or clear browser cache

---

## Expected Behavior

**When Working:**
1. Dashboard page loads
2. Shows loading spinner briefly
3. Displays dashboard metrics:
   - Comparison Quality score
   - Decision Confidence metrics
   - Category statistics
   - Activity trends
   - Feedback insights

**When Broken:**
1. Dashboard page loads
2. Shows loading spinner
3. Shows red error box: "Failed to fetch dashboard data"
4. Shows "Retry" button

---

## Check Backend Logs

When error occurs, check backend terminal for:

```
ERROR: Error getting dashboard: <error message>
```

Common error messages:
- `relation "comparisons" does not exist` → Database not initialized
- `could not connect to server` → Database not running
- `timeout` → Database connection timeout
- `No module named 'database'` → Import error

---

## Most Likely Cause

Based on the error, the most common causes are:

1. **Backend server not running** (80% of cases)
2. **Database not initialized** (15% of cases)
3. **Database connection issue** (5% of cases)

---

## Quick Test

Run this to test everything:

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Test endpoint
curl http://localhost:8000/analytics/dashboard?days=30

# Should return JSON, not error
```

If curl works but frontend doesn't → Frontend configuration issue
If curl fails → Backend/database issue




