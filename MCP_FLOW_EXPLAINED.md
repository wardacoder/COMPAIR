# MCP Flow - Detailed Explanation

## The Complete Flow with Code References

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: User asks question                                  │
│ "What's the quality score?"                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: MCP Client sends to Groq LLM                       │
│ File: grok_mcp_client.py, Line 149                          │
│                                                             │
│ response = client.chat.completions.create(...)            │
│                                                             │
│ What's sent:                                                │
│ - System prompt (with tool list)                           │
│ - User question                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Groq LLM responds with TEXT                       │
│ File: grok_mcp_client.py, Line 156                          │
│                                                             │
│ assistant_message = "TOOL_CALL:get_comparison_quality"     │
│                                                             │
│ ⚠️ IMPORTANT: This is just TEXT, not a function call!    │
│ The LLM doesn't call anything - it just returns text.     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: MCP Client CODE detects pattern                    │
│ File: grok_mcp_client.py, Line 159                          │
│                                                             │
│ if "TOOL_CALL:" in assistant_message:                      │
│     # Python code checks if text contains "TOOL_CALL:"     │
│                                                             │
│ This is PATTERN DETECTION - Python code checking text!     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Extract tool name                                   │
│ File: grok_mcp_client.py, Line 163                          │
│                                                             │
│ tool_name = "get_comparison_quality"                       │
│                                                             │
│ Python code extracts the tool name from the text.          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: MCP Client CODE calls invoke_mcp_tool()            │
│ File: grok_mcp_client.py, Line 166                          │
│                                                             │
│ tool_result = invoke_mcp_tool(tool_name)                  │
│                                                             │
│ ⚠️ This is PYTHON CODE executing, NOT the LLM!           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: invoke_mcp_tool() makes HTTP request               │
│ File: grok_mcp_client.py, Line 64-68                        │
│                                                             │
│ response = requests.post(                                   │
│     "http://localhost:8001/tools/invoke",                  │
│     json={"tool_name": "get_comparison_quality"}           │
│ )                                                           │
│                                                             │
│ ⚠️ This is PYTHON CODE making HTTP request!                │
│ The LLM is NOT involved here at all!                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: MCP Server receives request                        │
│ File: mcp_server.py, Line 587-616                           │
│                                                             │
│ 1. Receives HTTP POST at /tools/invoke                      │
│ 2. Looks up tool in TOOLS registry                         │
│ 3. Executes tool function                                  │
│ 4. Queries database                                         │
│ 5. Returns JSON response                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 9: MCP Client receives data                            │
│ File: grok_mcp_client.py, Line 69-72                        │
│                                                             │
│ result = response.json()                                    │
│ tool_result = {"comprehensiveness_score": 4.3, ...}        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 10: MCP Client sends data BACK to Groq LLM           │
│ File: grok_mcp_client.py, Line 175-181                      │
│                                                             │
│ follow_up = "The tool returned this data: {...}"           │
│ messages.append({"role": "user", "content": follow_up})    │
│                                                             │
│ ⚠️ Now we're talking to the LLM AGAIN!                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 11: Groq LLM formats final answer                     │
│ File: grok_mcp_client.py, Line 183-190                      │
│                                                             │
│ final_response = client.chat.completions.create(...)       │
│                                                             │
│ Returns: "The quality score is 4.3/5..."                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 12: User sees formatted answer                        │
│ "The comparison quality score is 4.3/5 based on 14        │
│  user responses. Users are generally satisfied..."          │
└─────────────────────────────────────────────────────────────┘
```

## Key Points to Remember:

1. **LLM does NOT directly call the server**
   - LLM only returns TEXT: "TOOL_CALL:get_comparison_quality"
   - Python code detects this pattern and makes the HTTP call

2. **Two conversations with LLM:**
   - First: LLM decides which tool to call
   - Second: LLM formats the final answer using tool data

3. **Pattern Detection:**
   - Line 159: `if "TOOL_CALL:" in assistant_message:`
   - This is simple string matching in Python code

4. **HTTP Request:**
   - Line 64: `requests.post(...)` 
   - This is Python's `requests` library making HTTP call
   - LLM is NOT involved in this step

5. **The LLM never directly talks to the MCP server**
   - All communication goes through the MCP Client Python code
   - MCP Client acts as a "translator" between LLM and server




