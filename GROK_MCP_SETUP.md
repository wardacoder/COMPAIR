# Grok MCP Client Setup Guide

This guide shows you how to connect Grok (via Groq) to the COMPAIR MCP server in the terminal.

## Prerequisites

1. **MCP Server Running**: The MCP server must be running on port 8001
2. **Groq API Key**: Free API key from Groq (used as the LLM backend)
3. **Python Dependencies**: `groq` library installed

## Step 1: Install Groq Library

```powershell
pip install groq
```

## Step 2: Get Groq API Key (Free)

1. Go to: https://console.groq.com/
2. Sign up for a free account
3. Create an API key
4. Copy the key

## Step 3: Start MCP Server

In one terminal:

```powershell
cd backend
$env:DATABASE_URL = "sqlite:///./compair.db"
python mcp_server.py
```

The server should start on `http://localhost:8001`

## Step 4: Set Groq API Key

In PowerShell:

```powershell
$env:GROQ_API_KEY = "your-groq-api-key-here"
```

## Step 5: Run Grok MCP Client

In another terminal:

```powershell
cd backend
$env:GROQ_API_KEY = "your-groq-api-key-here"
python grok_mcp_client.py
```

## Usage

Once running, you can ask questions like:

- "What's the comparison quality score?"
- "How many users provided feedback?"
- "What are the most compared categories?"
- "Show me user feedback insights"
- "What are the trends in comparison activity?"
- "Generate an insights report"

The client will automatically:
1. Detect when a tool is needed
2. Call the appropriate MCP tool
3. Use the data to provide an intelligent answer

## Available Commands

- `tools` - List all available MCP tools
- `quit` or `exit` or `q` - Exit the client

## Troubleshooting

### "Could not connect to MCP server"
- Make sure the MCP server is running on port 8001
- Check: `http://localhost:8001/tools` in your browser

### "GROQ_API_KEY not set"
- Set the environment variable: `$env:GROQ_API_KEY = "your-key"`

### "Groq library not installed"
- Run: `pip install groq`

## Example Session

```
🤖 COMPAIR Grok MCP Client
======================================================================
✅ Connecting to MCP server at http://localhost:8001...
✅ Found 9 MCP tools
💡 Ask me anything about COMPAIR dashboard analytics!

You: What's the comparison quality score?
🔧 Calling MCP tool: get_comparison_quality
🤖 Grok: The comparison quality score is 4.1/5 based on 14 user responses...
```

## Note

This uses Groq (free LLM service) as the backend. When xAI's Grok API becomes publicly available, the script can be easily adapted to use it instead.






