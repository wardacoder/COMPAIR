# 🚀 COMPAIR - How to Start All Services

This guide shows you how to start the **Frontend**, **Backend**, and **MCP Server** manually.

---

## 📋 Prerequisites

Make sure you have:
- ✅ Python 3.9+ installed
- ✅ Node.js 16+ installed  
- ✅ SQLite database (default) or PostgreSQL configured
- ✅ Environment variables set (see below)

---

## 🔧 Step 1: Set Environment Variables

### For Windows (PowerShell):

```powershell
# Set OpenAI API Key (required)
$env:OPENAI_API_KEY = "your-openai-api-key-here"

# Set Groq API Key (for MCP analytics chat - optional)
$env:GROQ_API_KEY = "your-groq-api-key-here"

# Set Database URL (defaults to SQLite if not set)
$env:DATABASE_URL = "sqlite:///./backend/compair.db"

# Set MCP Server URL (for analytics chat)
$env:MCP_SERVER_URL = "http://localhost:8001"

# Set Brave Search API Key (optional)
$env:BRAVE_API_KEY = "your-brave-api-key-here"
```

### For Linux/Mac:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export GROQ_API_KEY="your-groq-api-key-here"
export DATABASE_URL="sqlite:///./backend/compair.db"
export MCP_SERVER_URL="http://localhost:8001"
export BRAVE_API_KEY="your-brave-api-key-here"
```

---

## 🗄️ Step 2: Initialize Database

```bash
# Navigate to backend directory
cd backend

# Initialize database (creates tables)
python database/init_db.py
```

**Expected output:**
```
✅ Database initialized successfully: sqlite:///./compair.db
```

---

## 🔙 Step 3: Start Backend Server

**Open Terminal 1:**

```bash
# Navigate to backend directory
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start backend server
python main.py
```

**Expected output:**
```
🚀 Starting COMPAIR Backend Server...
✅ Database initialized successfully
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Backend will be available at:** `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

---

## 🤖 Step 4: Start MCP Server

**Open Terminal 2:**

```bash
# Navigate to backend directory
cd backend

# Start MCP server
python mcp_server.py
```

**Expected output:**
```
🚀 Starting COMPAIR MCP Server v2.0 on 0.0.0.0:8001
📊 Dashboard-aligned tools: 11
   • get_dashboard_overview
   • get_comparison_quality
   ...
```

**MCP Server will be available at:** `http://localhost:8001`
- Tools List: `http://localhost:8001/tools`
- Health Check: `http://localhost:8001/health`

---

## 🎨 Step 5: Start Frontend

**Open Terminal 3:**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Start frontend development server
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view react-basics in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**Frontend will be available at:** `http://localhost:3000`
- Main App: `http://localhost:3000`
- Dashboard: `http://localhost:3000/dashboard`

---

## ✅ Step 6: Verify All Services

### Check Backend:
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy",...}`

### Check MCP Server:
```bash
curl http://localhost:8001/health
```
Should return: `{"status":"healthy",...}`

### Check Frontend:
Open browser: `http://localhost:3000`

---

## 📊 Quick Test

1. **Test Comparison:**
   - Go to `http://localhost:3000`
   - Enter 2 items (e.g., "iPhone 15" vs "Samsung S24")
   - Select category (e.g., "Gadgets")
   - Click "Compare"
   - Should see comparison results

2. **Test Dashboard:**
   - Go to `http://localhost:3000/dashboard`
   - Should see analytics dashboard with metrics

3. **Test MCP Tools:**
   - Go to `http://localhost:8001/tools`
   - Should see list of available tools

---

## 🛑 Stopping Services

To stop each service:
- **Backend (Terminal 1):** Press `Ctrl+C`
- **MCP Server (Terminal 2):** Press `Ctrl+C`
- **Frontend (Terminal 3):** Press `Ctrl+C`

---

## 🐛 Troubleshooting

### Backend won't start:
- ✅ Check if port 8000 is available
- ✅ Verify `OPENAI_API_KEY` is set
- ✅ Check database initialization: `python backend/database/init_db.py`
- ✅ Check logs for errors

### MCP Server won't start:
- ✅ Check if port 8001 is available
- ✅ Verify backend is running first (MCP needs database)
- ✅ Check `DATABASE_URL` is set correctly

### Frontend won't start:
- ✅ Check if port 3000 is available
- ✅ Run `npm install` if dependencies missing
- ✅ Check `frontend/src/config/api.js` has correct backend URL

### Database errors:
- ✅ Make sure database is initialized: `python backend/database/init_db.py`
- ✅ Check database file exists: `backend/compair.db` (for SQLite)
- ✅ Verify `DATABASE_URL` environment variable

---

## 📝 Summary

**Three terminals needed:**

| Terminal | Command | Port | URL |
|----------|---------|------|-----|
| Terminal 1 | `cd backend && python main.py` | 8000 | http://localhost:8000 |
| Terminal 2 | `cd backend && python mcp_server.py` | 8001 | http://localhost:8001 |
| Terminal 3 | `cd frontend && npm start` | 3000 | http://localhost:3000 |

**Order to start:**
1. ✅ Set environment variables
2. ✅ Initialize database
3. ✅ Start Backend (Terminal 1)
4. ✅ Start MCP Server (Terminal 2)
5. ✅ Start Frontend (Terminal 3)

---

**Need help?** Check the logs in each terminal for error messages!



