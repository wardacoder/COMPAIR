# Quick Fix: Analytics Chat Error

## Error Message
"Sorry, I couldn't process that question. Please make sure the MCP server is running on port 8001 and GROQ_API_KEY is set."

## Issue Found
✅ **MCP Server:** Running (port 8001)  
❌ **GROQ_API_KEY:** NOT SET

---

## Quick Fix

### Step 1: Get Free Groq API Key

1. Go to: https://console.groq.com/
2. Sign up (it's free!)
3. Click "API Keys" → "Create API Key"
4. Copy the key (starts with `gsk_`)

### Step 2: Set Environment Variable

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY = "your-groq-api-key-here"
```

**Windows CMD:**
```cmd
set GROQ_API_KEY=your-groq-api-key-here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

### Step 3: Restart Backend

**Important:** You MUST restart the backend after setting the environment variable!

1. Stop backend (Ctrl+C in backend terminal)
2. Set GROQ_API_KEY (see Step 2)
3. Start backend again:
   ```bash
   cd backend
   python main.py
   ```

### Step 4: Test

1. Refresh Dashboard page
2. Try asking: "How is the COMPAIR platform performing?"
3. Should work now! ✅

---

## Verify Setup

### Check if GROQ_API_KEY is set:
```powershell
echo $env:GROQ_API_KEY
```

Should show your API key (starts with `gsk_`)

### Check if MCP Server is running:
Open in browser: http://localhost:8001/health

Should see: `{"status": "healthy", ...}`

---

## Permanent Setup (Optional)

To make GROQ_API_KEY persistent, add it to your `.env` file:

**File:** `backend/.env`
```env
GROQ_API_KEY=your-groq-api-key-here
```

Then backend will load it automatically (if using python-dotenv).

---

## Summary

**Problem:** GROQ_API_KEY not set  
**Solution:** Set environment variable and restart backend  
**Time:** 2 minutes

After setting GROQ_API_KEY and restarting backend, the Analytics Chat should work! 🚀




