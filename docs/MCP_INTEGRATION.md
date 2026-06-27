# COMPAIR MCP Integration Guide

## Overview

The **Model Context Protocol (MCP)** server in COMPAIR exposes backend data as programmatic tools that ChatGPT can use to interpret data, identify patterns, and provide intelligent personalized recommendations.

Similar to how Canva uses MCP to make sense of user content, COMPAIR's MCP server allows AI assistants to:
- Query comparison history
- Analyze analytics and trends
- Access feedback insights
- Generate personalized recommendations

## Architecture

```
┌─────────────────┐       ┌─────────────────┐       ┌──────────────────┐
│                 │       │                 │       │                  │
│   ChatGPT       │◄─────►│   MCP Server    │◄─────►│   PostgreSQL     │
│   (AI Agent)    │       │   (Port 8001)   │       │   (Database)     │
│                 │       │                 │       │                  │
└─────────────────┘       └─────────────────┘       └──────────────────┘
         │                         │
         │                         │
         ▼                         ▼
    Interprets Data        Exposes Tools
    Generates Insights     Fetches Data
    Provides Recommendations
```

## MCP Server Setup

### 1. Installation

The MCP server is already included in the backend. No additional dependencies are required beyond the main `requirements.txt`.

### 2. Running the MCP Server

#### Option A: Standalone Mode

```bash
cd backend
python mcp_server.py
```

The MCP server will start on `http://0.0.0.0:8001`

#### Option B: Docker Compose (Recommended)

Add the following service to `docker-compose.yml`:

```yaml
  mcp:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: compair-mcp
    environment:
      DATABASE_URL: ${DATABASE_URL}
      MCP_HOST: 0.0.0.0
      MCP_PORT: 8001
    ports:
      - "8001:8001"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: python mcp_server.py
    restart: always
```

Then run:
```bash
docker-compose up -d mcp
```

### 3. Environment Variables

Add to your `.env` file:

```env
# MCP Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8001
```

## Available MCP Tools

### 1. `get_comparison_history`

Retrieve a user's comparison history to understand their preferences and patterns.

**Parameters:**
- `user_id` (string, required): User identifier
- `limit` (integer, optional): Maximum number of results (default: 20)
- `category` (string, optional): Filter by category

**Example Request:**
```json
{
  "tool_name": "get_comparison_history",
  "parameters": {
    "user_id": "user123",
    "limit": 10,
    "category": "gadgets"
  }
}
```

**Example Response:**
```json
{
  "tool_name": "get_comparison_history",
  "success": true,
  "data": {
    "user_id": "user123",
    "comparison_count": 10,
    "history": [
      {
        "id": "abc123",
        "category": "gadgets",
        "items": ["iPhone 15", "Samsung S24"],
        "result": {...},
        "created_at": "2024-01-15T10:30:00"
      }
    ]
  }
}
```

### 2. `get_analytics_summary`

Get comprehensive analytics summary with trends and metrics.

**Parameters:**
- `days` (integer, optional): Number of days to analyze (default: 30)

**Example:**
```json
{
  "tool_name": "get_analytics_summary",
  "parameters": {
    "days": 30
  }
}
```

### 3. `get_trending_items`

Get currently trending comparisons and most compared items.

**Parameters:** None

**Returns:**
- List of trending shared comparisons
- Most compared items with counts

### 4. `get_feedback_insights`

Get user feedback insights and satisfaction metrics.

**Parameters:**
- `days` (integer, optional): Number of days to analyze (default: 30)

**Returns:**
- Total feedback count
- Average rating
- Rating distribution
- Helpful/accurate percentages

### 5. `get_winner_patterns`

Understand which items are most frequently selected as winners.

**Parameters:**
- `days` (integer, optional): Number of days to analyze (default: 30)

**Returns:**
- Winner distribution with items, counts, and percentages

### 6. `get_category_insights`

Get category usage insights and trends.

**Parameters:**
- `days` (integer, optional): Number of days to analyze (default: 30)

**Returns:**
- Category statistics with counts

### 7. `get_personalized_recommendations`

Generate personalized recommendations based on user history and patterns.

**Parameters:**
- `user_id` (string, required): User identifier
- `context` (string, optional): Context for recommendations

**Returns:**
- User's favorite categories
- Frequently compared items
- Preference patterns
- Personalized recommendations

## Integrating with ChatGPT

### Step 1: Configure ChatGPT Custom GPT

1. Go to ChatGPT → Custom GPTs → Create
2. Add the following instruction:

```
You are a COMPAIR analytics assistant. You have access to tools that query the COMPAIR database.

Available tools:
- get_comparison_history: Get user's past comparisons
- get_analytics_summary: Get overall analytics
- get_trending_items: Get trending comparisons
- get_feedback_insights: Get user feedback data
- get_winner_patterns: Get winner statistics
- get_category_insights: Get category usage
- get_personalized_recommendations: Generate recommendations

Use these tools to:
1. Answer questions about user behavior
2. Identify patterns and trends
3. Provide data-driven insights
4. Generate personalized recommendations

When a user asks about their comparisons, trends, or needs recommendations, 
use the appropriate tool and interpret the results in a helpful, conversational way.
```

### Step 2: Add API Configuration

Configure the MCP server endpoint:
- **Base URL**: `http://your-server:8001`
- **Authentication**: None (add if needed)

### Step 3: Example Interactions

**User:** "What have I been comparing lately?"

**ChatGPT Action:**
```json
POST /tools/invoke
{
  "tool_name": "get_comparison_history",
  "parameters": {
    "user_id": "user123",
    "limit": 5
  }
}
```

**ChatGPT Response:**
"Based on your recent comparisons, you've been primarily focused on gadgets. In the last 5 comparisons, you compared:
1. iPhone 15 vs Samsung S24
2. MacBook Pro vs Dell XPS
3. ...

You seem to prioritize performance and battery life. Would you like recommendations for similar products?"

## Use Cases

### 1. Personal Shopping Assistant

ChatGPT can analyze your comparison history and recommend products based on your preferences:

```
User: "I need a new laptop for video editing"
ChatGPT: *Uses get_comparison_history + get_personalized_recommendations*
"Based on your past comparisons, you prioritize performance and display quality.
I recommend the MacBook Pro M3 because..."
```

### 2. Trend Analysis

ChatGPT can identify market trends and popular products:

```
User: "What's trending in gadgets?"
ChatGPT: *Uses get_trending_items + get_category_insights*
"Currently, smartphones are the most compared category, with iPhone 15 
being the most popular item with 234 comparisons..."
```

### 3. Quality Insights

ChatGPT can provide feedback on comparison quality:

```
User: "How are our comparisons performing?"
ChatGPT: *Uses get_feedback_insights*
"Overall, comparisons have a 4.5/5 average rating with 85% helpful ratings.
Users particularly appreciate the personalized recommendations..."
```

## API Reference

### List All Tools

```http
GET /tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "get_comparison_history",
      "description": "Get user's comparison history...",
      "parameters": {...}
    }
  ],
  "count": 7
}
```

### Invoke a Tool

```http
POST /tools/invoke
Content-Type: application/json

{
  "tool_name": "get_analytics_summary",
  "parameters": {
    "days": 30
  }
}
```

**Response:**
```json
{
  "tool_name": "get_analytics_summary",
  "success": true,
  "data": {...},
  "error": null
}
```

### Health Check

```http
GET /health
```

## Security Considerations

### Current Implementation (Development)
- No authentication required
- Open CORS policy
- Suitable for local development

### Production Recommendations

1. **Add API Key Authentication:**
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.getenv("MCP_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

2. **Restrict CORS:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],  # Only ChatGPT
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

3. **Rate Limiting:**
```python
from slowapi import Limiter
limiter = Limiter(key_func=lambda: "global")

@app.post("/tools/invoke")
@limiter.limit("10/minute")
async def invoke_tool(request: ToolRequest):
    ...
```

4. **User Authorization:**
Verify that the requesting user has permission to access specific user data.

## Monitoring & Debugging

### Enable Detailed Logging

```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Monitor Tool Usage

Track which tools are being called most frequently:

```python
from collections import defaultdict

tool_usage_stats = defaultdict(int)

@app.post("/tools/invoke")
async def invoke_tool(request: ToolRequest):
    tool_usage_stats[request.tool_name] += 1
    # ... rest of the code
```

### Health Monitoring

Check MCP server health:
```bash
curl http://localhost:8001/health
```

## Troubleshooting

### Issue: MCP server not starting
**Solution:** Check if port 8001 is available
```bash
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows
```

### Issue: Tools not accessible from ChatGPT
**Solution:** Ensure CORS is properly configured and server is publicly accessible

### Issue: Database connection errors
**Solution:** Verify DATABASE_URL environment variable is set correctly

### Issue: Slow tool responses
**Solution:** 
- Add database indexes
- Implement caching
- Optimize queries

## Next Steps

1. **Extend Tools:** Add more specialized tools based on user needs
2. **Add Caching:** Cache frequently accessed data
3. **Implement Webhooks:** Notify ChatGPT of new comparisons
4. **Add ML Models:** Integrate recommendation models
5. **Create Dashboard:** Monitor MCP tool usage

## Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [OpenAI Custom GPTs](https://help.openai.com/en/articles/8554397-creating-a-gpt)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For questions or issues, please refer to:
- Main README.md
- Backend documentation in `/docs`
- Database schema in `/docs/DATABASE_IMPLEMENTATION.md`

