# COMPAIR Features Overview

This document provides an overview of the three key features added to COMPAIR: **Dashboard**, **Feedback**, and **MCP Integration**.

## Table of Contents

1. [Dashboard - Visual Analytics](#dashboard---visual-analytics)
2. [Feedback System](#feedback-system)
3. [MCP - ChatGPT Integration](#mcp---chatgpt-integration)
4. [Quick Start](#quick-start)
5. [Architecture](#architecture)

---

## Dashboard - Visual Analytics

### Overview

The Dashboard provides comprehensive visual analytics and insights into comparison usage, trends, and quality metrics.

### Features

#### 📊 Key Metrics
- **Total Comparisons**: Overall number of comparisons made
- **Active Users**: Number of unique users
- **Average Rating**: Mean user feedback rating (1-5 stars)
- **Quality Score**: Percentage of helpful ratings

#### 📈 Visual Charts
1. **Most Compared Items**: Top items by comparison count
2. **Category Distribution**: Usage breakdown by category
3. **Winner Distribution**: Most frequently selected winners
4. **Trends Over Time**: Daily comparison counts
5. **Feedback Ratings**: Star rating distribution

#### ⏱️ Time Range Filters
- Last 7 days
- Last 30 days
- Last 90 days
- Last year

### Access

Navigate to `/dashboard` or click "Dashboard" in the navigation menu.

### API Endpoints

```http
GET /analytics/dashboard?days=30
GET /analytics/trends?days=30
GET /analytics/winner-distribution?days=30
GET /analytics/feedback-stats?days=30
GET /analytics/category-stats?days=30
```

### Screenshots

```
┌─────────────────────────────────────────────────────┐
│  📊 Analytics Dashboard                              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│  │  1,234 │ │   145  │ │  4.5★  │ │  85%   │       │
│  │Compares│ │ Users  │ │ Rating │ │Quality │       │
│  └────────┘ └────────┘ └────────┘ └────────┘       │
│                                                      │
│  Most Compared Items        Category Usage          │
│  ▓▓▓▓▓▓▓▓▓▓░░ iPhone 15     ▓▓▓▓░░ Gadgets (40%)   │
│  ▓▓▓▓▓▓▓░░░░ Samsung S24     ▓▓▓░░░ Cars (30%)     │
│                                                      │
│  Trends Over Time (Last 30 Days)                    │
│  ▅ ▆ ▇ █ ▆ ▅ ▄ ▅ ▆ ▇ ▆ ▅ ▄ ▅                      │
└─────────────────────────────────────────────────────┘
```

---

## Feedback System

### Overview

The Feedback System allows users to rate and comment on each comparison, helping improve quality and providing valuable user insights.

### Features

#### ⭐ Star Rating
- 1-5 star rating system
- Visual feedback for each rating level
- Average rating calculation

#### 💬 Comments
- Optional text feedback
- Display of community comments
- Timestamp for each review

#### ✅ Quality Indicators
- "This comparison was helpful" checkbox
- "The information was accurate" checkbox
- Aggregate quality metrics

#### 📊 Feedback Analytics
- Total feedback count
- Average rating
- Rating distribution (1-5 stars)
- Helpful percentage
- Accurate percentage

### User Flow

1. User completes a comparison
2. Feedback section appears below results
3. User selects star rating (required)
4. User adds optional comment
5. User checks quality indicators
6. User submits feedback
7. Feedback is stored and aggregated

### Implementation

#### Backend Models

```python
class Feedback(Base):
    id = Column(String(36), primary_key=True)
    comparison_id = Column(String(36), ForeignKey("comparisons.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    helpful = Column(Boolean, default=True)
    accurate = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### API Endpoints

```http
POST /feedback
  Body: {
    "comparison_id": "abc123",
    "rating": 5,
    "comment": "Very helpful!",
    "user_id": "user123",
    "helpful": true,
    "accurate": true
  }

GET /feedback/{comparison_id}
  Returns: List of all feedback for a comparison

GET /analytics/feedback-stats?days=30
  Returns: Aggregate feedback statistics
```

#### Frontend Component

```jsx
<FeedbackSection 
  comparisonId={result.comparison_id} 
  userId="guest123"
/>
```

### Feedback Display

```
┌─────────────────────────────────────────────────────┐
│  💬 Rate This Comparison                             │
│                                                      │
│  How would you rate this comparison?                │
│  ⭐ ⭐ ⭐ ⭐ ⭐  Excellent! ⭐                          │
│                                                      │
│  Additional Comments (Optional)                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ This comparison helped me decide...          │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ✓ This comparison was helpful                      │
│  ✓ The information was accurate                     │
│                                                      │
│  [ Submit Feedback ]                                │
│                                                      │
│  ─────────────────────────────────────────────────  │
│                                                      │
│  Community Feedback                                 │
│  ⭐ 4.5 / 5  (127 reviews)                          │
│                                                      │
│  ⭐⭐⭐⭐⭐  2024-01-15                                │
│  "This comparison helped me decide..."              │
│  ✓ Helpful  ✓ Accurate                             │
└─────────────────────────────────────────────────────┘
```

---

## MCP - ChatGPT Integration

### Overview

The Model Context Protocol (MCP) server exposes COMPAIR data as programmatic tools that ChatGPT can use to interpret data, identify patterns, and provide intelligent recommendations.

### Key Concept

Similar to how Canva uses MCP to understand user designs, COMPAIR's MCP allows ChatGPT to:
- **Access Data**: Query comparison history, analytics, and feedback
- **Identify Patterns**: Find trends in user behavior
- **Provide Insights**: Generate data-driven recommendations
- **Assist Users**: Act as an intelligent shopping assistant

### Available Tools

#### 1. get_comparison_history
Query a user's past comparisons to understand preferences.

**Use Case:**
```
User: "What have I been comparing?"
ChatGPT: Queries history and responds with personalized insights
```

#### 2. get_analytics_summary
Get comprehensive analytics including trends and metrics.

**Use Case:**
```
User: "How is COMPAIR performing?"
ChatGPT: Provides overview of usage, popular items, categories
```

#### 3. get_trending_items
Discover what's currently popular.

**Use Case:**
```
User: "What are people comparing in gadgets?"
ChatGPT: Lists trending gadget comparisons
```

#### 4. get_feedback_insights
Understand user satisfaction and quality metrics.

**Use Case:**
```
User: "Are users happy with the comparisons?"
ChatGPT: Reports average ratings and quality scores
```

#### 5. get_winner_patterns
Identify most frequently selected winners.

**Use Case:**
```
User: "Which phones are winning most comparisons?"
ChatGPT: Shows winner distribution with percentages
```

#### 6. get_category_insights
Analyze category usage trends.

**Use Case:**
```
User: "What categories are most popular?"
ChatGPT: Displays category breakdown and trends
```

#### 7. get_personalized_recommendations
Generate intelligent recommendations based on user history.

**Use Case:**
```
User: "Recommend a laptop for video editing"
ChatGPT: Analyzes history, preferences, and suggests best match
```

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     ChatGPT / AI Agent                    │
│  - Interprets natural language queries                   │
│  - Decides which MCP tools to use                        │
│  - Synthesizes results into conversational responses     │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     ▼
┌──────────────────────────────────────────────────────────┐
│              MCP Server (Port 8001)                       │
│  - Exposes 7 tools as HTTP endpoints                     │
│  - Validates requests and parameters                     │
│  - Fetches data from database                            │
│  - Returns structured JSON responses                     │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ SQL Queries
                     ▼
┌──────────────────────────────────────────────────────────┐
│              PostgreSQL Database                          │
│  - Stores comparisons, feedback, analytics               │
│  - Indexed for fast queries                              │
│  - Provides raw data for analysis                        │
└──────────────────────────────────────────────────────────┘
```

### Example Interaction

**User Query:**
> "I need help choosing between iPhone 15 and Samsung S24"

**ChatGPT Action:**
1. Calls `get_comparison_history` with user's ID
2. Calls `get_winner_patterns` for phones category
3. Calls `get_feedback_insights` for these items

**ChatGPT Response:**
> "Based on your past comparisons, you prioritize camera quality and battery life. 
> Looking at recent trends, the iPhone 15 wins 65% of comparisons when users 
> prioritize camera quality. However, the Samsung S24 has a 4.8/5 rating for 
> battery life vs iPhone's 4.3/5. 
> 
> Since you care most about camera quality (based on your previous comparisons 
> of cameras and photo equipment), I'd recommend the iPhone 15. It excels in 
> low-light photography and video recording, which aligns with your preferences."

### Setup

1. **Start MCP Server:**
```bash
python backend/mcp_server.py
```

2. **Configure ChatGPT Custom GPT:**
- Add MCP server URL: `http://your-server:8001`
- Configure available tools
- Set system prompt

3. **Test Connection:**
```bash
curl http://localhost:8001/tools
```

### Security

**Development:**
- No authentication (localhost only)
- Open CORS

**Production:**
- API key authentication
- Restricted CORS to ChatGPT domains
- Rate limiting
- User authorization checks

For detailed MCP documentation, see [MCP_INTEGRATION.md](./MCP_INTEGRATION.md)

---

## Quick Start

### 1. Database Migration

The new features require database schema updates:

```bash
cd backend
python database/init_db.py
```

This creates the `feedback` table and necessary indexes.

### 2. Start All Services

```bash
# Start main backend (Port 8000)
cd backend
uvicorn main:app --reload

# Start MCP server (Port 8001)
python mcp_server.py

# Start frontend (Port 3000)
cd ../frontend
npm start
```

Or use Docker Compose:

```bash
docker-compose up -d
```

### 3. Access Features

- **Dashboard**: http://localhost:3000/dashboard
- **Feedback**: Appears automatically after comparisons
- **MCP Tools**: http://localhost:8001/tools

---

## Architecture

### System Overview

```
┌────────────────────────────────────────────────────────────┐
│                      Frontend (React)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Home   │  │ Compare  │  │Dashboard │  │ History  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                      │              │                       │
│                      └──────┬───────┘                       │
└─────────────────────────────┼──────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌────────────────────────────────────────────────────────────┐
│                 Backend API (FastAPI - Port 8000)          │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  /compare        │  │  /feedback       │               │
│  │  /history        │  │  /analytics/*    │               │
│  └──────────────────┘  └──────────────────┘               │
└────────────────────────────────┬───────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
┌─────────────────────────────────┐  ┌──────────────────────┐
│  MCP Server (Port 8001)         │  │  PostgreSQL Database │
│  - 7 Tools for ChatGPT          │  │  - Comparisons       │
│  - Analytics queries            │  │  - Feedback          │
│  - Recommendation engine        │  │  - Users             │
└─────────────────────────────────┘  │  - Analytics Cache   │
              │                       └──────────────────────┘
              │                                  │
              └──────────────────────────────────┘
```

### Data Flow

#### 1. User Submits Comparison
```
User → Frontend → POST /compare → Backend → OpenAI GPT → Database
                                                          ↓
User ← Frontend ← Response ← Result ← AI Response ← Cache Check
```

#### 2. User Submits Feedback
```
User → Frontend → POST /feedback → Backend → Database
                                              ↓
                                     Aggregate Stats Updated
```

#### 3. User Views Dashboard
```
User → Frontend → GET /analytics/dashboard → Backend → Database
                                                         ↓
User ← Frontend ← Dashboard Data ← Aggregated Metrics
```

#### 4. ChatGPT Queries Data
```
ChatGPT → MCP Server → POST /tools/invoke → Database
                                             ↓
ChatGPT ← Response ← Tool Result ← Query Results
```

---

## Technology Stack

### Backend
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **LangChain**: AI/LLM integration
- **OpenAI GPT**: Comparison generation

### Frontend
- **React**: UI framework
- **React Router**: Navigation
- **Tailwind CSS**: Styling
- **Lucide React**: Icons
- **Framer Motion**: Animations

### MCP Server
- **FastAPI**: HTTP server
- **Pydantic**: Request/response validation
- **PostgreSQL**: Data source

---

## API Reference

### Feedback Endpoints

#### Submit Feedback
```http
POST /feedback
Content-Type: application/json

{
  "comparison_id": "uuid",
  "rating": 5,
  "comment": "Very helpful!",
  "user_id": "user123",
  "helpful": true,
  "accurate": true
}
```

#### Get Feedback
```http
GET /feedback/{comparison_id}

Response:
{
  "comparison_id": "uuid",
  "feedback_count": 10,
  "feedback": [...]
}
```

### Analytics Endpoints

#### Dashboard Summary
```http
GET /analytics/dashboard?days=30

Response:
{
  "total_comparisons": 1234,
  "total_users": 145,
  "most_compared_items": [...],
  "category_stats": [...],
  "feedback_stats": {...},
  "trends": [...],
  "winner_distribution": [...]
}
```

#### Trends
```http
GET /analytics/trends?days=30

Response:
{
  "trends": [
    {"date": "2024-01-15", "count": 45},
    ...
  ]
}
```

### MCP Endpoints

#### List Tools
```http
GET /tools

Response:
{
  "tools": [...],
  "count": 7
}
```

#### Invoke Tool
```http
POST /tools/invoke
Content-Type: application/json

{
  "tool_name": "get_analytics_summary",
  "parameters": {"days": 30}
}

Response:
{
  "tool_name": "get_analytics_summary",
  "success": true,
  "data": {...}
}
```

---

## Performance Considerations

### Database Optimization
- Indexes on frequently queried columns
- JSONB for PostgreSQL (better performance than JSON)
- Composite indexes for common query patterns
- Connection pooling

### Caching
- Comparison results cached for 24 hours
- Analytics aggregations cached
- Redis integration recommended for production

### Query Optimization
- Eager loading to prevent N+1 queries
- Limited result sets with pagination
- Date range filtering to reduce data volume

---

## Future Enhancements

### Dashboard
- [ ] Real-time updates using WebSockets
- [ ] Export dashboard as PDF/Excel
- [ ] Custom dashboard widgets
- [ ] A/B testing metrics

### Feedback
- [ ] Feedback moderation system
- [ ] Reply to feedback comments
- [ ] Feedback sentiment analysis
- [ ] Automated quality alerts

### MCP
- [ ] More sophisticated ML-based recommendations
- [ ] Integration with more AI platforms
- [ ] Webhook notifications for real-time updates
- [ ] Custom tool creation API

---

## Support & Documentation

- **Main README**: [../README.md](../README.md)
- **MCP Integration**: [MCP_INTEGRATION.md](./MCP_INTEGRATION.md)
- **Database Schema**: [DATABASE_IMPLEMENTATION.md](./DATABASE_IMPLEMENTATION.md)
- **API Documentation**: http://localhost:8000/docs (when running)
- **MCP API Documentation**: http://localhost:8001/docs (when running)

---

## Contributors

Created as part of the COMPAIR enhancement project to add visual analytics, user feedback, and intelligent AI integration capabilities.

