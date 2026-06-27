# Speaking Points: main.py vs mcp_server.py Endpoints

## Quick Summary

**main.py (Port 8000)** = User application API  
**mcp_server.py (Port 8001)** = AI assistant tools API

---

## main.py Endpoints (Port 8000)

**Purpose:** Complete COMPAIR application for end users

**Key Endpoints:**
- `POST /compare` - Main comparison feature (uses AI, search, caching)
- `POST /ask-followup` - Follow-up questions (conversational AI)
- `POST /share-comparison` - Create shareable links
- `GET /analytics/dashboard` - Dashboard analytics
- `POST /feedback` - User feedback system

**Total:** 17 endpoints covering all app features

**Functionality:**
- ✅ AI-powered comparisons
- ✅ Real-time search integration
- ✅ Caching and optimization
- ✅ Sharing and analytics
- ✅ User feedback system

**Who uses it:** Frontend React application (users)

---

## mcp_server.py Endpoints (Port 8001)

**Purpose:** MCP protocol server for AI assistants

**Key Endpoints:**
- `GET /tools` - List available tools (9 tools)
- `POST /tools/invoke` - Execute a tool (main endpoint)
- `GET /health` - Health check

**Total:** 4 endpoints (MCP protocol standard)

**Functionality:**
- ✅ Exposes dashboard data as tools
- ✅ Simple tool invocation pattern
- ✅ Returns raw analytics data
- ✅ Read-only (queries only, no writes)

**Who uses it:** AI assistants (ChatGPT, Claude, Grok via MCP clients)

---

## Key Differences

| Feature | main.py | mcp_server.py |
|---------|---------|----------------|
| **Port** | 8000 | 8001 |
| **Endpoints** | 17 | 4 |
| **Purpose** | User app | AI tools |
| **Complexity** | High | Low |
| **Protocol** | REST API | MCP Protocol |
| **Data** | Full comparisons | Analytics only |
| **Writes** | Yes (creates comparisons) | No (read-only) |

---

## When Each is Called

### main.py Flow:
```
User → Frontend → POST /compare → AI generates comparison → User sees result
```

### mcp_server.py Flow:
```
User asks Grok → Grok decides tool → POST /tools/invoke → Database query → Grok formats answer
```

---

## One-Liner Summary

**main.py:** "Complete app API for users to create comparisons"  
**mcp_server.py:** "Simple tool API for AI assistants to query dashboard data"




