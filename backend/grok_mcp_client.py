"""
COMPAIR Grok MCP Client

A terminal-based chat interface using Groq (free LLM) that connects to the MCP server
to answer questions about COMPAIR dashboard analytics.

Usage:
    1. Make sure MCP server is running: python mcp_server.py
    2. Set GROQ_API_KEY: $env:GROQ_API_KEY = "your-key-here"
    3. Run: python grok_mcp_client.py
    
Get free Groq API key: https://console.groq.com/
"""

import os
import json
import requests
from typing import Dict, List, Optional

# Groq API setup (can be replaced with xAI Grok API when available)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq library not installed. Install with: pip install groq")

# MCP Server URL
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

# Color codes for terminal
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def get_mcp_tools() -> List[Dict]:
    """Get list of available MCP tools from the server."""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/tools", timeout=5)
        if response.status_code == 200:
            return response.json().get("tools", [])
        return []
    except Exception as e:
        print(f"{Colors.RED}❌ Error connecting to MCP server: {e}{Colors.END}")
        return []


def invoke_mcp_tool(tool_name: str, parameters: Dict = None) -> Dict:
    """Invoke an MCP tool on the server."""
    if parameters is None:
        parameters = {}
    
    try:
        payload = {
            "tool_name": tool_name,
            "parameters": parameters
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
        return {"error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def format_tools_for_prompt(tools: List[Dict]) -> str:
    """Format tools list for LLM prompt."""
    if not tools:
        return "No tools available."
    
    tool_descriptions = []
    for tool in tools:
        name = tool.get("name", "")
        desc = tool.get("description", "")
        tool_descriptions.append(f"- {name}: {desc}")
    return "\n".join(tool_descriptions)


def chat_with_groq(user_message: str, conversation_history: List[Dict], tools: List[Dict]) -> str:
    """Chat with Groq LLM, automatically using MCP tools when needed."""
    
    if not GROQ_AVAILABLE:
        return "❌ Groq library not installed. Run: pip install groq"
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ GROQ_API_KEY not set. Get a free key from https://console.groq.com/\nSet it with: $env:GROQ_API_KEY = 'your-key-here'"
    
    # Clean the API key (remove any whitespace)
    api_key = api_key.strip()
    
    # Validate API key format
    if not api_key.startswith("gsk_"):
        return f"❌ Invalid API key format. Should start with 'gsk_'\nYour key starts with: '{api_key[:4] if len(api_key) >= 4 else 'empty'}'\nGet your key from: https://console.groq.com/keys"
    
    try:
        client = Groq(api_key=api_key)
        
        # Build system prompt with tool information
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
5. Be helpful, insightful, and provide actionable recommendations

CRITICAL RESPONSE GUIDELINES:
- For AREAS OF IMPROVEMENT (low scores, declining trends, negative feedback):
  * Always identify the specific problem clearly
  * Provide concrete, actionable ways to mitigate or improve the issue
  * Suggest specific steps, features, or changes that could help
  * Be constructive and solution-oriented

- For STRENGTHS (high scores, positive trends, good metrics):
  * Acknowledge what's working well
  * Encourage the user to keep up the good work
  * Suggest how to maintain or amplify these positive trends
  * Highlight why these strengths matter

Example responses:
- If quality score is low: "The comparison quality score is 2.8/5, which needs improvement. To mitigate this: 1) Enhance comparison detail depth, 2) Add more product attributes, 3) Improve AI prompt engineering for better comprehensiveness. Consider gathering specific user feedback on what's missing."
- If quality score is high: "Excellent! Your comparison quality score is 4.6/5 - users are very satisfied. Keep up this great work by maintaining detailed comparisons and continuing to gather user feedback to stay aligned with expectations."

Example:
User: "What's the comparison quality score?"
You: TOOL_CALL:get_comparison_quality
(I execute tool and give you results)
You: "The comparison quality score is 4.3/5 based on 14 user responses..." """
        
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
        
        # Check if LLM wants to call a tool
        if "TOOL_CALL:" in assistant_message:
            # Extract tool name
            tool_line = [line for line in assistant_message.split("\n") if "TOOL_CALL:" in line]
            if tool_line:
                tool_name = tool_line[0].replace("TOOL_CALL:", "").strip()
                
                # Invoke tool (silently)
                tool_result = invoke_mcp_tool(tool_name)
                
                # Format tool result for LLM
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
                
                return final_response.choices[0].message.content
        
        return assistant_message
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "invalid_api_key" in error_msg.lower():
            return f"""❌ Invalid API Key Error

This usually means:
1. The API key is incorrect or expired
2. The key wasn't copied completely
3. The key has been revoked

Troubleshooting:
1. Go to: https://console.groq.com/keys
2. Create a NEW API key
3. Copy it COMPLETELY (should be long, starts with 'gsk_')
4. Set it: $env:GROQ_API_KEY = 'your-complete-key-here'
5. Verify: echo $env:GROQ_API_KEY (should show your key)

Current key (first 10 chars): {api_key[:10] if api_key else 'NOT SET'}...
"""
        return f"❌ Error: {error_msg}"


def main():
    """Main chat loop."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 70)
    print("🤖 COMPAIR Grok MCP Client")
    print("=" * 70)
    print(f"{Colors.END}")
    print(f"{Colors.GREEN}✅ Connecting to MCP server at {MCP_SERVER_URL}...{Colors.END}")
    
    # Get available tools
    tools = get_mcp_tools()
    if not tools:
        print(f"{Colors.RED}❌ Could not connect to MCP server. Is it running?{Colors.END}")
        print(f"{Colors.YELLOW}💡 Start it with:{Colors.END}")
        print(f"{Colors.YELLOW}   cd backend{Colors.END}")
        print(f"{Colors.YELLOW}   $env:DATABASE_URL = 'sqlite:///./compair.db'{Colors.END}")
        print(f"{Colors.YELLOW}   python mcp_server.py{Colors.END}")
        return
    
    print(f"{Colors.GREEN}✅ Found {len(tools)} MCP tools{Colors.END}")
    print(f"{Colors.CYAN}💡 Ask me anything about COMPAIR dashboard analytics!{Colors.END}")
    print(f"{Colors.YELLOW}💡 Type 'quit', 'exit', or 'q' to leave{Colors.END}")
    print(f"{Colors.YELLOW}💡 Type 'tools' to see available tools{Colors.END}\n")
    
    # Check Groq setup
    if not GROQ_AVAILABLE:
        print(f"{Colors.RED}❌ Groq library not installed.{Colors.END}")
        print(f"{Colors.YELLOW}Install with: pip install groq{Colors.END}")
        return
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(f"{Colors.RED}❌ GROQ_API_KEY not set.{Colors.END}")
        print(f"{Colors.YELLOW}1. Get a free API key from: https://console.groq.com/{Colors.END}")
        print(f"{Colors.YELLOW}2. Set it in PowerShell:{Colors.END}")
        print(f"{Colors.YELLOW}   $env:GROQ_API_KEY = 'your-key-here'{Colors.END}")
        return
    
    # Conversation history
    conversation_history = []
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input(f"\n{Colors.BOLD}{Colors.CYAN}You: {Colors.END}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"{Colors.BLUE}👋 Goodbye!{Colors.END}")
                break
            
            if user_input.lower() == 'tools':
                print(f"\n{Colors.BOLD}Available MCP Tools:{Colors.END}")
                for i, tool in enumerate(tools, 1):
                    print(f"{Colors.CYAN}{i}. {tool.get('name', 'Unknown')}{Colors.END}")
                    print(f"   {tool.get('description', 'No description')}")
                continue
            
            # Get response
            print(f"{Colors.BLUE}🤖 Grok: {Colors.END}", end="", flush=True)
            response = chat_with_groq(user_input, conversation_history, tools)
            print(response)
            
            # Update history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
            
            # Keep history manageable (last 20 messages = 10 exchanges)
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
                
        except KeyboardInterrupt:
            print(f"\n{Colors.BLUE}👋 Goodbye!{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")


if __name__ == "__main__":
    main()

