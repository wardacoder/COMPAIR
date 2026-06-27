# ============================================================================
# ANALYTICS CHAT ENDPOINT - Add this to backend/main.py
# ============================================================================
# This endpoint enables frontend chat interface for dashboard analytics
# using Groq LLM and MCP tools
# ============================================================================

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
        - conversation_history: Updated conversation history
    
    Use: Dashboard analytics chat interface in frontend
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
        
        # Update conversation history
        updated_history = conversation_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
        
        return {
            "answer": assistant_message,
            "tool_used": tool_used,
            "conversation_history": updated_history
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")




