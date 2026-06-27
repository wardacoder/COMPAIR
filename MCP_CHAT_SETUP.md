# COMPAIR MCP Chat Assistant - Setup Guide

## Step 1: Install Groq Library

```powershell
pip install groq
```

## Step 2: Get Free Groq API Key

1. Go to: https://console.groq.com/
2. Sign up (it's free!)
3. Create an API key
4. Copy the key

## Step 3: Set Environment Variable

In PowerShell:

```powershell
$env:GROQ_API_KEY = "your-api-key-here"
```

## Step 4: Make Sure MCP Server is Running

In one terminal:

```powershell
cd backend
$env:DATABASE_URL = "sqlite:///./compair.db"
python mcp_server.py
```

## Step 5: Run the Chat Assistant

In another terminal:

```powershell
cd backend
python grok_mcp_client.py
```

## Usage

Once running, you can ask questions like:

- "What's the current comparison quality score?"
- "Generate an insights report"
- "How are users using preferences?"
- "What feedback have users given?"
- "Show me activity trends"

The assistant will automatically use MCP tools to answer!

## Example Conversation

```
You: What's the comparison quality?
🤖 Assistant: 🔧 Calling MCP tool: get_comparison_quality
The current comparison quality score is 4.55/5, which is excellent...
```




