# COMPAIR Endpoints Guide

## Overview

COMPAIR has **two separate servers** with different purposes:

1. **main.py** (Port 8000) - Main application API for users
2. **mcp_server.py** (Port 8001) - MCP protocol server for AI assistants

---

## 📋 Table of Contents

- [main.py Endpoints (Port 8000)](#mainpy-endpoints-port-8000)
- [mcp_server.py Endpoints (Port 8001)](#mcpserverpy-endpoints-port-8001)
- [When Each Endpoint is Called](#when-each-endpoint-is-called)
- [Key Differences](#key-differences)

---

## main.py Endpoints (Port 8000)

**Purpose:** Main COMPAIR application API - handles user-facing features

### Health & Status Endpoints

| Endpoint | Method | Purpose | When Called |
|----------|--------|---------|-------------|
| `/` | GET | Basic API health check | Server startup verification |
| `/health` | GET | Server status check | Health monitoring, load balancers |
| `/health/db` | GET | Database connection status | Database health monitoring |

### Core Comparison Endpoints

| Endpoint | Method | Purpose | When Called |
|----------|--------|---------|-------------|
| `/compare` | POST | **Main endpoint** - Compare items using AI | User submits comparison form |
| `/ask-followup` | POST | Ask follow-up questions about comparison | User asks question in chat interface |
| `/followup-history/{comparison_id}` | GET | Get conversation history | Load chat history in UI |

### Sharing Endpoints

| Endpoint | Method | Purpose | When Called |
|----------|--------|---------|-------------|
| `/share-comparison` | POST | Create shareable link | User clicks "Share" button |
| `/shared/{share_id}` | GET | Retrieve shared comparison | Someone opens shared link |

### Analytics Endpoints

| Endpoint | Method | Purpose | When Called |
|----------|--------|---------|-------------|
| `/analytics/dashboard` | GET | Comprehensive dashboard data | Dashboard page loads |
| `/analytics/trending` | GET | Trending shared comparisons | Homepage trending section |
| `/analytics/popular-items` | GET | Most compared items | Popular items section |
| `/analytics/category-stats` | GET | Statistics by category | Category analytics page |
| `/analytics/trends` | GET | Time-based trends | Trend charts |
| `/analytics/winner-distribution` | GET | Winner statistics | Winner charts |
| `/analytics/feedback-stats` | GET | Aggregate feedback metrics | Feedback dashboard |

### Feedback Endpoints

| Endpoint | Method | Purpose | When Called |
|----------|--------|---------|-------------|
| `/feedback` | POST | Submit feedback for comparison | User submits rating/comment |
| `/feedback/{comparison_id}` | GET | Get feedback for comparison | Display feedback on page |

**Total: 17 endpoints**

---

## mcp_server.py Endpoints (Port 8001)

**Purpose:** MCP (Model Context Protocol) server - exposes dashboard data as tools for AI assistants

### MCP Protocol Endpoints

| Endpoint | Method | Purpose | When Called |
|----------|--------|---------|-------------|
| `/` | GET | MCP server info | Server discovery |
| `/health` | GET | MCP server health check | Health monitoring |
| `/tools` | GET | List all available MCP tools | MCP client startup (discovers tools) |
| `/tools/invoke` | POST | **Main endpoint** - Execute an MCP tool | AI assistant needs dashboard data |

**Total: 4 endpoints**

---

## When Each Endpoint is Called

### User Flow (main.py - Port 8000)

```
1. User opens app
   → Frontend calls: GET /health
   
2. User submits comparison form
   → Frontend calls: POST /compare
   → Backend: Uses OpenAI GPT, Brave Search, returns comparison
   
3. User asks follow-up question
   → Frontend calls: POST /ask-followup
   → Backend: Uses OpenAI GPT with context, returns answer
   
4. User clicks "Share"
   → Frontend calls: POST /share-comparison
   → Backend: Creates shareable link
   
5. Someone opens shared link
   → Frontend calls: GET /shared/{share_id}
   → Backend: Returns comparison, increments view count
   
6. Dashboard page loads
   → Frontend calls: GET /analytics/dashboard
   → Backend: Queries database, returns comprehensive stats
   
7. User submits feedback
   → Frontend calls: POST /feedback
   → Backend: Saves feedback to database
```

### AI Assistant Flow (mcp_server.py - Port 8001)

```
1. MCP Client starts
   → Calls: GET /tools
   → Server: Returns list of 9 available tools
   
2. User asks Grok: "What's the quality score?"
   → Grok LLM decides: "I need get_comparison_quality tool"
   → MCP Client calls: POST /tools/invoke
   → Body: {"tool_name": "get_comparison_quality", "parameters": {}}
   → Server: Executes tool → Queries database → Returns data
   → MCP Client: Sends data to Grok → Grok formats answer
   
3. User asks: "Generate insights report"
   → Grok decides: "I need generate_insights_report tool"
   → MCP Client calls: POST /tools/invoke
   → Server: Executes tool → Queries database → Returns comprehensive report
   → Grok formats answer
```

---

## Key Differences

### main.py (Port 8000) - User Application API

**Characteristics:**
- ✅ **User-facing** - Frontend React app calls these
- ✅ **Full features** - Comparisons, sharing, follow-ups, analytics
- ✅ **Complex logic** - AI integration, caching, search, validation
- ✅ **Rich responses** - Structured comparison objects, conversation history
- ✅ **17 endpoints** - Complete application functionality

**Example Request:**
```json
POST http://localhost:8000/compare
{
  "category": "gadgets",
  "items": ["iPhone 15", "Samsung S24"],
  "user_preferences": {
    "budget": "$1000",
    "priorities": ["camera", "battery"]
  }
}
```

**Example Response:**
```json
{
  "introduction": "...",
  "table": [...],
  "pros": {...},
  "cons": {...},
  "recommendation": "...",
  "personalized_winner": "iPhone 15",
  "comparison_id": "abc-123"
}
```

---

### mcp_server.py (Port 8001) - MCP Protocol Server

**Characteristics:**
- ✅ **AI-facing** - AI assistants (ChatGPT, Claude, Grok) call these
- ✅ **Tool-based** - Exposes dashboard data as programmatic tools
- ✅ **Simple interface** - Standard MCP protocol (tools/invoke pattern)
- ✅ **Data-focused** - Returns raw dashboard metrics
- ✅ **4 endpoints** - Minimal MCP protocol implementation

**Example Request:**
```json
POST http://localhost:8001/tools/invoke
{
  "tool_name": "get_comparison_quality",
  "parameters": {}
}
```

**Example Response:**
```json
{
  "tool_name": "get_comparison_quality",
  "success": true,
  "data": {
    "comprehensiveness_score": 4.3,
    "rating_breakdown": {"5": 10, "4": 4},
    "total_responses": 14,
    "quality_assessment": "Good - Users are generally satisfied..."
  }
}
```

---

## Summary Table

| Aspect | main.py (8000) | mcp_server.py (8001) |
|--------|----------------|----------------------|
| **Purpose** | User application API | AI assistant tools |
| **Audience** | Frontend React app | AI assistants (ChatGPT, Claude, Grok) |
| **Endpoints** | 17 endpoints | 4 endpoints |
| **Complexity** | High (AI, search, caching) | Low (data queries) |
| **Protocol** | REST API | MCP Protocol |
| **Data Flow** | User → Frontend → Backend → AI → Response | AI → MCP Client → MCP Server → Database → Response |
| **Use Case** | Complete app functionality | Dashboard analytics for AI |

---

## Quick Reference

### Most Important Endpoints

**main.py:**
- `POST /compare` - Main comparison endpoint
- `POST /ask-followup` - Follow-up questions
- `GET /analytics/dashboard` - Dashboard data

**mcp_server.py:**
- `GET /tools` - List available tools
- `POST /tools/invoke` - Execute tool (most important!)

---

## Notes

1. **Both servers can run simultaneously** - They're on different ports
2. **Both query the same database** - PostgreSQL database
3. **Different purposes** - main.py for users, mcp_server.py for AI
4. **MCP server is optional** - Main app works without it
5. **MCP server is read-only** - Only queries data, doesn't create comparisons




