# Frontend MCP Integration Guide

## Overview

Yes! The MCP/Grok chat can be integrated into the frontend. Here's how:

**Current Setup:**
- Terminal-based: `grok_mcp_client.py` (command line)
- User types in terminal → Grok answers

**New Setup:**
- Frontend-based: React component → Backend endpoint → Grok + MCP tools → Frontend displays

---

## Architecture

```
User (Frontend) 
  → POST /analytics/chat 
  → Backend (main.py) 
  → Groq LLM + MCP Tools 
  → Database queries 
  → Formatted answer 
  → Frontend displays
```

**Benefits:**
- ✅ No terminal needed
- ✅ Beautiful UI in browser
- ✅ API keys stay secure (backend only)
- ✅ Same chat interface as follow-up questions

---

## Implementation Steps

### Step 1: Create Backend Endpoint

Add to `backend/main.py`:

```python
# --------------------------------------------------------------------------
# ANALYTICS CHAT ENDPOINT - MCP-powered dashboard chat
# --------------------------------------------------------------------------
@app.post("/analytics/chat")
async def analytics_chat(request: dict):
    """
    Chat with AI assistant about dashboard analytics using MCP tools.
    
    URL: POST /analytics/chat
    
    Request Body:
        - message: User's question about dashboard
        - conversation_history: Optional list of previous messages
    
    Returns:
        - answer: AI's response
        - tool_used: Optional tool name if MCP tool was called
    
    Use: Dashboard analytics chat interface
    """
    try:
        import os
        import json
        import requests
        from typing import Dict, List
        
        # Check if Groq is available
        try:
            from groq import Groq
            GROQ_AVAILABLE = True
        except ImportError:
            raise HTTPException(
                status_code=503,
                detail="Groq library not installed. Install with: pip install groq"
            )
        
        # Get API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="GROQ_API_KEY not set. Set it as environment variable."
            )
        
        user_message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # MCP Server URL
        MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
        
        # Get available tools from MCP server
        try:
            tools_response = requests.get(f"{MCP_SERVER_URL}/tools", timeout=5)
            if tools_response.status_code == 200:
                tools = tools_response.json().get("tools", [])
            else:
                tools = []
        except Exception as e:
            logger.warning(f"Could not connect to MCP server: {e}")
            tools = []
        
        # Format tools for prompt
        def format_tools_for_prompt(tools: List[Dict]) -> str:
            if not tools:
                return "No tools available."
            tool_descriptions = []
            for tool in tools:
                name = tool.get("name", "")
                desc = tool.get("description", "")
                tool_descriptions.append(f"- {name}: {desc}")
            return "\n".join(tool_descriptions)
        
        # Invoke MCP tool
        def invoke_mcp_tool(tool_name: str) -> Dict:
            try:
                payload = {
                    "tool_name": tool_name,
                    "parameters": {}
                }
                response = requests.post(
                    f"{MCP_SERVER_URL}/tools/invoke",
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return result.get("data", {})
                    else:
                        return {"error": result.get("error", "Unknown error")}
                return {"error": f"HTTP {response.status_code}"}
            except Exception as e:
                return {"error": str(e)}
        
        # Initialize Groq client
        client = Groq(api_key=api_key.strip())
        
        # Build system prompt
        system_prompt = f"""You are an intelligent analytics assistant for COMPAIR, a product comparison platform.

You have access to these tools to analyze dashboard data:
{format_tools_for_prompt(tools)}

When the user asks about:
- Dashboard overview, general metrics → use get_dashboard_overview or generate_insights_report
- Quality scores, ratings, comprehensiveness → use get_comparison_quality
- Decision making, winner matching → use get_decision_confidence
- User preferences (personalized vs general) → use get_preference_usage
- Category statistics → use get_category_insights
- Popular comparisons → use get_popular_comparisons
- User feedback, comments → use get_user_feedback_summary
- Trends, activity over time → use get_activity_trends
- General insights and recommendations → use generate_insights_report

IMPORTANT INSTRUCTIONS:
1. When the user asks a question that requires data, you MUST call the appropriate tool FIRST
2. To call a tool, respond with EXACTLY: TOOL_CALL:tool_name
3. I will execute the tool and give you the results
4. Then provide a clear, conversational answer using that data
5. Be helpful, insightful, and provide actionable recommendations"""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # Call Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        assistant_message = response.choices[0].message.content
        tool_used = None
        
        # Check if LLM wants to call a tool
        if "TOOL_CALL:" in assistant_message:
            # Extract tool name
            tool_line = [line for line in assistant_message.split("\n") if "TOOL_CALL:" in line]
            if tool_line:
                tool_name = tool_line[0].replace("TOOL_CALL:", "").strip()
                tool_used = tool_name
                
                # Invoke tool
                tool_result = invoke_mcp_tool(tool_name)
                
                # Format tool result
                if "error" in tool_result:
                    tool_data = f"Error: {tool_result['error']}"
                else:
                    tool_data = json.dumps(tool_result, indent=2)
                
                # Get final answer with tool data
                follow_up = f"""The tool '{tool_name}' returned this data:
{tool_data}

Now provide a clear, conversational answer to the user's question using this data. Be specific and insightful."""
                
                messages.append({"role": "assistant", "content": assistant_message})
                messages.append({"role": "user", "content": follow_up})
                
                final_response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1500
                )
                
                assistant_message = final_response.choices[0].message.content
        
        logger.info(f"💬 Analytics chat: {user_message[:50]}...")
        
        return {
            "answer": assistant_message,
            "tool_used": tool_used,
            "conversation_history": conversation_history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message}
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")
```

### Step 2: Create Frontend Component

Create `frontend/src/components/AnalyticsChat.jsx`:

```jsx
import { useState } from "react";
import { BarChart3, Send, Loader2, Sparkles } from "lucide-react";
import API_BASE from "../config/api";

export default function AnalyticsChat() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userQuestion = question.trim();
    setQuestion("");
    
    // Add user message immediately
    const userMsg = {
      role: "user",
      content: userQuestion
    };
    setMessages(prev => [...prev, userMsg]);

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/analytics/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userQuestion,
          conversation_history: conversationHistory
        })
      });

      const data = await response.json();

      // Add AI response
      const assistantMsg = {
        role: "assistant",
        content: data.answer,
        tool_used: data.tool_used
      };
      setMessages(prev => [...prev, assistantMsg]);

      // Update conversation history
      setConversationHistory(data.conversation_history || []);

    } catch (error) {
      console.error("Analytics chat error:", error);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, I couldn't process that question. Please make sure the MCP server is running."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8 p-6 bg-gradient-to-br from-purple-50 to-indigo-50 
      dark:from-slate-800 dark:to-slate-900 rounded-2xl border-2 border-purple-200 
      dark:border-purple-800 shadow-lg">
      
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
          <BarChart3 className="w-6 h-6 text-purple-600 dark:text-purple-400" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100">
            Dashboard Analytics Assistant
          </h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Ask questions about COMPAIR analytics and metrics
          </p>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="space-y-3 mb-4 max-h-96 overflow-y-auto">
        {messages.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm font-medium mb-2">Ask me about dashboard analytics!</p>
            <div className="mt-3 space-y-2 text-xs">
              <p className="italic">"What's the comparison quality score?"</p>
              <p className="italic">"Generate an insights report"</p>
              <p className="italic">"How are users using preferences?"</p>
              <p className="italic">"Show me activity trends"</p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-2xl ${
                msg.role === "user"
                  ? "bg-purple-600 text-white rounded-br-none"
                  : "bg-white dark:bg-slate-700 text-gray-800 dark:text-gray-100 border border-gray-200 dark:border-slate-600 rounded-bl-none"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              {msg.tool_used && (
                <p className="text-xs mt-2 opacity-70 italic">
                  🔧 Used tool: {msg.tool_used}
                </p>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 
              p-3 rounded-2xl rounded-bl-none">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Analyzing dashboard data...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleAsk} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about dashboard analytics..."
          disabled={loading}
          className="flex-1 p-3 border border-gray-300 dark:border-slate-600 rounded-full 
            bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100
            focus:ring-2 focus:ring-purple-400 focus:border-purple-400 
            dark:focus:ring-purple-500 transition-all
            disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={!question.trim() || loading}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 
            text-white rounded-full font-medium shadow-md
            hover:from-purple-700 hover:to-indigo-700 
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all duration-300 flex items-center gap-2"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span className="hidden sm:inline">Ask</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
```

### Step 3: Add to Dashboard Page

Add to `frontend/src/pages/Dashboard.jsx`:

```jsx
import AnalyticsChat from "../components/AnalyticsChat";

// In the Dashboard component, add:
<AnalyticsChat />
```

---

## Setup Requirements

### 1. Install Groq Library

```bash
pip install groq
```

### 2. Set Environment Variables

```bash
# In backend/.env or environment
GROQ_API_KEY=your-groq-api-key-here
MCP_SERVER_URL=http://localhost:8001  # Optional, defaults to this
```

### 3. Make Sure MCP Server is Running

```bash
cd backend
python mcp_server.py
```

---

## Usage Flow

```
1. User opens Dashboard page
2. User types: "What's the quality score?"
3. Frontend → POST /analytics/chat
4. Backend → Groq LLM decides: "TOOL_CALL:get_comparison_quality"
5. Backend → Calls MCP server → Gets data
6. Backend → Groq formats answer
7. Frontend displays answer
```

---

## Benefits

✅ **Beautiful UI** - Same chat interface as follow-up questions  
✅ **Secure** - API keys stay on backend  
✅ **Integrated** - Part of main app, not separate terminal  
✅ **User-friendly** - No command line needed  
✅ **Consistent** - Same UX as rest of app  

---

## Example Questions Users Can Ask

- "What's the comparison quality score?"
- "Generate an insights report"
- "How are users using preferences?"
- "What categories are most popular?"
- "Show me activity trends"
- "What feedback have users given?"
- "Are comparisons helping users decide?"

---

## Notes

- MCP server must be running (port 8001)
- Groq API key must be set
- Same conversation history tracking as follow-up chat
- Tool usage is shown in UI (which MCP tool was called)




