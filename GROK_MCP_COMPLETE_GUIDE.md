# Complete Step-by-Step Guide: Grok MCP Client Setup

## 🎯 Goal
Connect Grok (via Groq) to your COMPAIR MCP server so you can chat about dashboard analytics in the terminal.

---

## Step 1: Get a Free Groq API Key

1. **Open your web browser**
2. **Go to:** https://console.groq.com/
3. **Sign up** (or sign in if you already have an account)
   - It's completely free
   - No credit card required
4. **Once logged in, go to API Keys:**
   - Click on "API Keys" in the left menu
   - Or go directly to: https://console.groq.com/keys
5. **Create a new API key:**
   - Click "Create API Key" button
   - Give it a name (e.g., "COMPAIR MCP")
   - Click "Submit"
6. **Copy the API key:**
   - It will look like: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **IMPORTANT:** Copy the ENTIRE key (it's long!)
   - Save it somewhere safe (you won't see it again)

---

## Step 2: Install Groq Library

Open PowerShell and run:

```powershell
pip install groq
```

Wait for it to install. You should see "Successfully installed groq..."

---

## Step 3: Start the MCP Server

The MCP server needs to be running for the client to connect to it.

1. **Open a PowerShell terminal**
2. **Navigate to the backend folder:**
   ```powershell
   cd C:\Users\warda\Downloads\COMPAIR\backend
   ```

3. **Set the database URL:**
   ```powershell
   $env:DATABASE_URL = "sqlite:///./compair.db"
   ```

4. **Start the MCP server:**
   ```powershell
   python mcp_server.py
   ```

5. **You should see:**
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8001
   ```

6. **Leave this terminal running** (don't close it!)

---

## Step 4: Set Your Groq API Key

1. **Open a NEW PowerShell terminal** (keep the MCP server running in the first one)

2. **Navigate to the backend folder:**
   ```powershell
   cd C:\Users\warda\Downloads\COMPAIR\backend
   ```

3. **Set your API key** (replace `gsk_your-actual-key-here` with the key you copied):
   ```powershell
   $env:GROQ_API_KEY = "gsk_your-actual-key-here"
   ```

   **Example:**
   ```powershell
   $env:GROQ_API_KEY = "gsk_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
   ```

4. **Verify it's set:**
   ```powershell
   echo $env:GROQ_API_KEY
   ```
   
   You should see your key (starts with `gsk_`)

---

## Step 5: Test Your API Key

Still in the same PowerShell terminal (where you set the key):

```powershell
python test_groq_key.py
```

**Expected output if successful:**
```
🔑 Testing API key: gsk_abc123...
✅ API key is valid!
✅ Response: Hello
🎉 You're ready to use grok_mcp_client.py!
```

**If you see an error:**
- Make sure you copied the entire key
- Make sure there are no extra spaces
- Try creating a new key from Groq console

---

## Step 6: Run the Grok MCP Client

Still in the same PowerShell terminal:

```powershell
python grok_mcp_client.py
```

**You should see:**
```
🤖 COMPAIR Grok MCP Client
======================================================================
✅ Connecting to MCP server at http://localhost:8001...
✅ Found 9 MCP tools
💡 Ask me anything about COMPAIR dashboard analytics!
💡 Type 'quit', 'exit', or 'q' to leave
💡 Type 'tools' to see available tools
```

---

## Step 7: Start Chatting!

Now you can ask questions like:

- `What's the comparison quality score?`
- `How many users provided feedback?`
- `What are the most compared categories?`
- `Show me user feedback insights`
- `Generate an insights report`

The client will automatically:
1. Detect when it needs data
2. Call the appropriate MCP tool
3. Give you an intelligent answer

---

## 📋 Quick Reference

### Two Terminals Needed:

**Terminal 1 - MCP Server:**
```powershell
cd C:\Users\warda\Downloads\COMPAIR\backend
$env:DATABASE_URL = "sqlite:///./compair.db"
python mcp_server.py
```
(Leave this running)

**Terminal 2 - Grok Client:**
```powershell
cd C:\Users\warda\Downloads\COMPAIR\backend
$env:GROQ_API_KEY = "gsk_your-actual-key-here"
python grok_mcp_client.py
```

---

## ❌ Troubleshooting

### "GROQ_API_KEY not set"
- Make sure you set it in the SAME terminal where you run the client
- Use: `$env:GROQ_API_KEY = "your-key"`

### "Could not connect to MCP server"
- Make sure MCP server is running in another terminal
- Check: http://localhost:8001/tools in your browser

### "Invalid API Key"
- Get a new key from: https://console.groq.com/keys
- Make sure you copied the ENTIRE key
- Make sure it starts with `gsk_`

### "Groq library not installed"
- Run: `pip install groq`

---

## 🎉 You're Done!

Once everything is working, you can chat with Grok about your COMPAIR dashboard analytics!






