# 🔑 Environment Variables Setup Guide

## Quick Answer

**If you have a `.env` file in the project root, you DON'T need to set variables in PowerShell!**

The backend automatically loads `.env` files using `python-dotenv`.

---

## 📍 Where Should `.env` File Be?

Create or edit `.env` file in the **project root** (same folder as `backend/` and `frontend/`):

```
COMPAIR/
├── .env          ← HERE (project root)
├── backend/
├── frontend/
└── ...
```

---

## ✅ Option 1: Use `.env` File (Recommended)

### Step 1: Create/Edit `.env` File

Create a file named `.env` in the project root with:

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional - for analytics chat feature
GROQ_API_KEY=your-groq-api-key-here

# Optional - defaults to SQLite if not set
DATABASE_URL=sqlite:///./backend/compair.db

# Optional - for real-time search
BRAVE_API_KEY=your-brave-api-key-here
```

### Step 2: That's It!

The backend automatically loads these when it starts. **No PowerShell commands needed!**

---

## ⚙️ Option 2: Use PowerShell (Alternative)

**Only use PowerShell if:**
- You don't want to create a `.env` file
- You want to override `.env` values temporarily
- You're testing different keys

### PowerShell Commands:

```powershell
# Required
$env:OPENAI_API_KEY = "your-openai-api-key-here"

# Optional - for analytics chat
$env:GROQ_API_KEY = "your-groq-api-key-here"

# Optional - defaults to SQLite if not set
$env:DATABASE_URL = "sqlite:///./backend/compair.db"
```

**Note:** PowerShell variables only last for that session. Close PowerShell = variables gone.

---

## 🔑 How to Get GROQ_API_KEY (Step-by-Step)

### Step 1: Go to Groq Console
Visit: **https://console.groq.com/keys**

### Step 2: Sign Up/Login
- Create a free account (if you don't have one)
- Sign in

### Step 3: Create API Key
- Click **"Create API Key"** or **"Generate Key"**
- Copy the key (it starts with `gsk_`)

### Step 4: Add to `.env` File
Add this line to your `.env` file:
```env
GROQ_API_KEY=gsk_your-actual-key-here
```

**OR** set in PowerShell:
```powershell
$env:GROQ_API_KEY = "gsk_your-actual-key-here"
```

---

## 📝 Complete `.env` File Example

Create `.env` in project root:

```env
# ============================================
# COMPAIR Environment Variables
# ============================================

# Required: OpenAI API Key (for comparisons)
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Optional: Groq API Key (for analytics chat)
GROQ_API_KEY=gsk_your-groq-key-here

# Optional: Database URL (defaults to SQLite)
DATABASE_URL=sqlite:///./backend/compair.db

# Optional: Brave Search API Key (for real-time search)
BRAVE_API_KEY=your-brave-key-here

# Optional: MCP Server URL (for analytics chat)
MCP_SERVER_URL=http://localhost:8001
```

---

## 🎯 Which Method Should You Use?

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **`.env` file** | ✅ Permanent<br>✅ Easy to manage<br>✅ Version control friendly | ❌ Need to create file | **Recommended** |
| **PowerShell** | ✅ Quick testing<br>✅ Temporary override | ❌ Lost when terminal closes<br>❌ Need to set each time | Testing only |

---

## ✅ Verification

### Check if `.env` is loaded:

```bash
# Start backend
cd backend
python main.py
```

Look for this in the output:
```
✅ Database initialized successfully
INFO: OpenAI key loaded successfully: True
```

If you see `True`, your `.env` file is working!

### Check if GROQ_API_KEY is set:

```bash
# In PowerShell
echo $env:GROQ_API_KEY

# Should show your key (or nothing if not set)
```

---

## 🚨 Common Issues

### Issue: Backend says "OPENAI_API_KEY not set"
**Fix:**
1. Check `.env` file exists in project root
2. Check `.env` file has `OPENAI_API_KEY=...` (no spaces around `=`)
3. Restart backend server

### Issue: Variables not loading from `.env`
**Fix:**
1. Make sure `.env` is in project root (not in `backend/` folder)
2. Check file is named exactly `.env` (not `.env.txt`)
3. Check no extra spaces: `OPENAI_API_KEY=value` (not `OPENAI_API_KEY = value`)

### Issue: PowerShell variables not working
**Fix:**
1. Make sure you're in the same PowerShell window
2. Variables reset when you close PowerShell
3. Use `.env` file instead for permanent setup

---

## 📋 Summary

**For your questions:**

1. **`OPENAI_API_KEY` in `.env`?** 
   - ✅ **NO PowerShell needed** - `.env` is automatically loaded

2. **`GROQ_API_KEY` steps?**
   - Get from: https://console.groq.com/keys
   - Add to `.env`: `GROQ_API_KEY=gsk_your-key-here`
   - ✅ **NO PowerShell needed** if in `.env`

3. **`DATABASE_URL` in `.env`?**
   - ✅ **NO PowerShell needed** - `.env` is automatically loaded

**Bottom line:** If it's in `.env`, you're done! 🎉



