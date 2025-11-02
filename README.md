# COMPAIR - AI-Powered Comparison Platform

A full-stack web application that uses AI to provide intelligent, detailed comparisons between products, destinations, technologies, and more.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Database Architecture](#database-architecture)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Docker Deployment](#docker-deployment)

---

## 🌟 Overview

COMPAIR is an intelligent comparison platform that leverages OpenAI's GPT-4 to generate comprehensive, structured comparisons between any two or more items. The application provides:

- **AI-Powered Comparisons**: Detailed analysis with pros, cons, feature tables, and recommendations
- **Real-Time Search Integration**: Uses Brave Search API to fetch accurate, up-to-date information and reduce hallucinations
- **Personalized Results**: Tailored recommendations based on user preferences
- **Comparison History**: Save and retrieve past comparisons
- **Share Functionality**: Generate shareable links for comparisons
- **Follow-up Questions**: Interactive Q&A about comparison results
- **Analytics**: Track trending comparisons and popular items
- **Caching**: Intelligent result caching for improved performance

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER REQUEST FLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Frontend   │
│ (React 18)  │
│  Port 3000  │
└──────┬───────┘
       │ HTTP/REST API
       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI - Port 8000)                       │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 1. Request Validation & Cache Check                               │  │
│  │    • Validate items, category, user preferences                  │  │
│  │    • Check PostgreSQL cache (24-hour TTL)                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                              │ (Cache miss)                               │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 2. Real-Time Data Fetching                                       │  │
│  │    • Brave Search API integration                                │  │
│  │    • Fetch search results for each item                          │  │
│  │    • Format results for LLM prompt                              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 3. LLM Processing (LangChain + OpenAI GPT-4o)                   │  │
│  │    • Construct prompt with search results                        │  │
│  │    • System message: Instructions + format                       │  │
│  │    • User message: Items + preferences + search data            │  │
│  │    • Parse structured JSON response                             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 4. Response Processing                                           │  │
│  │    • Cache result in PostgreSQL (24 hours)                       │  │
│  │    • Store in-memory conversation session                       │  │
│  │    • Return structured comparison                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────────────────────────────┘
               │
               │ Database Operations
               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL 15 Database                                 │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────────────┐   │
│  │   comparisons   │  │ comparison_  │  │   shared_comparisons   │   │
│  │                 │  │     cache    │  │                         │   │
│  │ • User history  │  │ • 24h TTL    │  │ • Public shares         │   │
│  │ • JSONB storage │  │ • JSONB      │  │ • View tracking         │   │
│  └─────────────────┘  └──────────────┘  └─────────────────────────┘   │
│                                                                          │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────────────┐   │
│  │   conversations │  │    items     │  │        users            │   │
│  │                 │  │              │  │                         │   │
│  │ • Follow-ups    │  │ • Analytics  │  │ • User preferences      │   │
│  │ • Chat history  │  │ • Popular    │  │ • Account data           │   │
│  └─────────────────┘  └──────────────┘  └─────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘

       │
       │ External API Calls
       ▼
┌──────────────────┐           ┌──────────────────┐
│   OpenAI API     │           │  Brave Search    │
│   (GPT-4o)       │           │      API         │
│                  │           │                  │
│ • LLM Inference  │           │ • Real-time      │
│ • Structured     │           │   search results │
│   Output         │           │ • Reduces        │
│                  │           │   hallucinations │
└──────────────────┘           └──────────────────┘
```

### Data Flow: Comparison Request Processing

```
1. User submits comparison request
   └─> Frontend sends POST /compare with items, category, preferences
       
2. Backend receives request
   └─> Validates input (items, category, length checks)
   └─> Checks PostgreSQL cache for existing comparison
       ├─> Cache HIT: Return cached result immediately (fast path)
       └─> Cache MISS: Continue to step 3
       
3. Real-time data fetching
   └─> Brave Search API called for each item
   └─> Results formatted and aggregated
   └─> Search data included in prompt
       
4. LLM processing
   └─> Prompt constructed:
       ├─> System Message: Instructions, format requirements, search emphasis
       └─> User Message: Items, preferences, REAL-TIME search results
   └─> OpenAI GPT-4o generates structured JSON response
   └─> Pydantic parser validates and structures output
       
5. Result handling
   └─> Cache result in PostgreSQL (24-hour expiration)
   └─> Create in-memory conversation session (for follow-ups)
   └─> Return structured comparison to frontend
```

### Component Architecture

#### 1. **Frontend (React Application)**

**Technology Stack**:
- **Framework**: React 18 with React Router
- **State Management**: React Hooks (useState, useEffect, Context API)
- **HTTP Client**: Fetch API
- **Styling**: CSS with theme toggle (light/dark mode)
- **Deployment**: Nginx serving static files in production

**Component Structure**:
```
src/
├── pages/
│   ├── Home.jsx          # Landing page
│   ├── Compare.jsx       # Main comparison interface
│   └── History.jsx       # User comparison history
├── components/
│   ├── CompareForm.jsx   # Input form with category tabs
│   ├── ResultDisplay.jsx # Comparison results display
│   ├── FollowUpChat.jsx # Interactive Q&A chat
│   ├── CategoryTabs.jsx  # Category selection
│   ├── ThemeToggle.jsx  # Dark/light mode switcher
│   └── Loader.jsx       # Loading indicators
└── config/
    └── api.js           # API endpoint configuration
```

**Key Features**:
- **Category-based comparison**: Gadgets, Cars, Technologies, Destinations, Shows, Other
- **Personalization**: User preferences (priorities, budget, use case)
- **Results visualization**: Feature tables, pros/cons lists, recommendations
- **Interactive chat**: Follow-up questions about comparisons
- **History management**: Save, view, and delete past comparisons
- **Share functionality**: Generate shareable links for comparisons
- **Theme support**: Light/dark mode with localStorage persistence

#### 2. **Backend (FastAPI Application)**

**Framework**: FastAPI (Python 3.x) with async support

**Core Module Structure**:

1. **`main.py`** - Application Entry Point
   - API route definitions (14 endpoints)
   - CORS middleware configuration
   - Request validation and error handling
   - LLM initialization and management
   - Health check endpoints (`/health`, `/health/db`)

2. **`prompt/prompt.py`** - LLM Prompt Engineering
   - **Comparison prompts**: Dynamic prompt generation with search results integration
   - **Follow-up prompts**: Context-aware Q&A templates
   - **Winner selection logic**: Personalized vs. balanced recommendations
   - **Format instructions**: Pydantic schema-based output formatting
   - **Anti-hallucination measures**: Strict instructions to use only search results

3. **`models/model.py`** - Request/Response Validation
   - Pydantic models for type safety
   - `CompareRequest`: Input validation (items, category, preferences)
   - `ComparisonOutput`: Structured output schema
   - `UserPreferences`: Preference validation
   - Request/response serialization

4. **`utilities/constants.py`** - Configuration Management
   - Environment variable loading
   - API keys (OpenAI, Brave Search)
   - Application constants (CORS, validation rules)
   - Configurable search parameters

5. **`utilities/brave_search.py`** - Real-Time Search Integration
   - **Search execution**: Parallel searches for multiple items
   - **Result formatting**: Structured data for LLM prompts
   - **Error handling**: Graceful fallback when search fails
   - **Configurable**: Count, snippets, timeout via environment variables
   - **Logging**: Detailed search statistics and debugging

6. **`utilities/storage.py`** - Data Access Layer
   - **Database abstraction**: Repository pattern implementation
   - **In-memory sessions**: Conversation memory for active sessions
   - **Cache management**: Cache lookup and storage operations
   - **History operations**: Save, load, delete comparisons
   - **Share management**: Create and retrieve shared comparisons

7. **`database/`** - Database Layer
   - **`models.py`**: SQLAlchemy ORM models (6 tables)
     - User, Comparison, SharedComparison, Conversation, ComparisonCache, Item
     - JSONB columns for flexible data storage (PostgreSQL)
     - Composite indexes for query optimization
   - **`connection.py`**: Database connection management
     - Connection pooling (20 persistent + 10 overflow)
     - Health checks and reconnection logic
     - Multi-database support (PostgreSQL/SQLite)
   - **`repository.py`**: CRUD operations
     - Optimized queries with eager loading
     - Cache management with TTL
     - Analytics queries (trending, popular items, category stats)
   - **`init_db.py`**: Database initialization and schema creation

**LangChain Integration**:
- **LLM**: OpenAI GPT-4o via `ChatOpenAI`
- **Output Parser**: `PydanticOutputParser` for structured JSON responses
- **Message Types**: `SystemMessage`, `HumanMessage`
- **Temperature**: 0.7 (configurable)
- **Chain Pattern**: Prompt → LLM → Parse → Validate

**API Endpoints** (14 total):
- **Core**: `/compare` (main comparison endpoint)
- **Storage**: `/save-comparison`, `/history/{user_id}`, `/delete-history/{user_id}/{comparison_id}`
- **Sharing**: `/share-comparison`, `/shared/{share_id}`
- **Interaction**: `/ask-followup`, `/followup-history/{comparison_id}`
- **Analytics**: `/analytics/trending`, `/analytics/popular-items`, `/analytics/category-stats`
- **Health**: `/`, `/health`, `/health/db`

#### 3. **Database (PostgreSQL 15)**

**Configuration**:
- **Image**: `postgres:15-alpine` (lightweight)
- **ORM**: SQLAlchemy 2.0 with declarative models
- **Storage Format**: JSONB for flexible schema (2-3x faster than JSON)
- **Connection Pooling**: 20 persistent + 10 overflow connections
- **Performance Tuning**: Optimized for 2GB RAM, SSD storage

**Database Schema** (6 tables):

1. **`users`**: User accounts and preferences
   - UUID primary key, email (unique), username, preferences (JSONB)

2. **`comparisons`**: User comparison history
   - Linked to users, stores category, items (JSONB), result (JSONB)
   - Composite index on (user_id, category, created_at)

3. **`shared_comparisons`**: Public shareable comparisons
   - Unique share_id (8 chars), view tracking, expiration support
   - Partial index for active shares

4. **`conversations`**: Follow-up question history
   - Linked to comparisons, stores messages (JSONB), original comparison snapshot

5. **`comparison_cache`**: 24-hour result caching
   - Stores category, items, preferences, result (all JSONB)
   - TTL-based expiration (24 hours default)
   - Partial index for cleanup operations

6. **`items`**: Popular items tracking
   - Item names, categories, comparison counts for analytics

**Key Features**:
- **JSONB Storage**: Efficient storage and querying of flexible JSON data
- **Composite Indexes**: Optimized for common query patterns
- **Partial Indexes**: PostgreSQL-specific optimizations
- **Automatic Cleanup**: Expired cache and shares cleanup
- **Health Monitoring**: Database connection and query health checks

#### 4. **External Services Integration**

**OpenAI GPT-4o**:
- **Purpose**: Generate structured comparison responses
- **Input**: Formatted prompt with search results, user preferences, category context
- **Output**: Structured JSON (validated via Pydantic)
- **Integration**: LangChain for prompt management and output parsing
- **Model**: GPT-4o with temperature 0.7
- **Output Format**: Pydantic-validated structured comparison schema

**Brave Search API**:
- **Purpose**: Fetch real-time, accurate product information to reduce hallucinations
- **Process**: Parallel searches executed for each item in comparison
- **Configuration**: 
  - Result count: Configurable (default: 5 results per item)
  - Snippet count: Configurable (default: 5 snippets in summary)
  - Timeout: Configurable (default: 10 seconds)
- **Output**: Formatted search snippets, descriptions, and source URLs
- **Integration**: Results embedded directly in LLM prompt as primary data source
- **Error Handling**: Graceful fallback with warnings if search fails

### Key Architectural Patterns

1. **Repository Pattern**: Database access abstracted through repository layer for maintainability
2. **Caching Strategy**: Two-tier caching system
   - PostgreSQL cache: 24-hour TTL for expensive LLM calls
   - In-memory sessions: Active conversation sessions (can migrate to Redis for scaling)
3. **Search-First Approach**: Brave Search results fetched and integrated before LLM processing
4. **Structured Output**: Pydantic models ensure type-safe API contracts and validation
5. **Graceful Degradation**: System works without search (with warnings), requires OpenAI
6. **Anti-Hallucination Measures**: Strict prompt instructions requiring use of only search results

---

## 🗄️ Database Architecture

### Entity-Relationship Diagram

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ id (PK)         │
│ email           │◄────────┐
│ username        │         │
│ preferences     │         │
│ created_at      │         │
│ updated_at      │         │
└─────────────────┘         │
        │                   │
        │ 1:N               │
        ▼                   │
┌─────────────────┐         │
│  Comparisons    │         │
├─────────────────┤         │
│ id (PK)         │         │
│ user_id (FK)    │─────────┘
│ category        │
│ items           │◄────────┐
│ result          │         │
│ created_at      │         │
└─────────────────┘         │
        │                   │
        │ 1:1               │
        ▼                   │
┌─────────────────┐         │
│ Conversations   │         │
├─────────────────┤         │
│ id (PK)         │         │
│ comparison_id(FK)─────────┘
│ user_id (FK)    │
│ messages        │
│ original_comp   │
│ items           │
│ category        │
│ created_at      │
│ updated_at      │
└─────────────────┘

┌─────────────────┐         ┌─────────────────┐
│SharedComparisons│         │ComparisonCache  │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │         │ id (PK)         │
│ share_id (UK)   │         │ category        │
│ comparison_id(FK)         │ items           │
│ user_id (FK)    │         │ user_preferences│
│ category        │         │ result          │
│ items           │         │ created_at      │
│ result          │         │ expires_at      │
│ views           │         └─────────────────┘
│ expires_at      │
│ created_at      │         ┌─────────────────┐
└─────────────────┘         │     Items       │
                            ├─────────────────┤
                            │ id (PK)         │
                            │ name (UK)       │
                            │ category        │
                            │ item_metadata   │
                            │ comparison_count│
                            │ created_at      │
                            │ updated_at      │
└─────────────────┘
```

### Database Tables

#### 1. **users**
Stores user account information and preferences.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID/String(36) | Primary key |
| `email` | String(255) | User email (unique, nullable) |
| `username` | String(255) | Display name |
| `preferences` | JSON | User preferences object |
| `created_at` | DateTime | Account creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Indexes**: `email` (unique)

#### 2. **comparisons**
Stores comparison history for users.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID/String(36) | Primary key |
| `user_id` | UUID/String(36) | Foreign key to users |
| `category` | String(100) | Comparison category |
| `items` | JSON | Array of items compared |
| `result` | JSON | Full comparison result |
| `created_at` | DateTime | Comparison timestamp |

**Indexes**: `user_id`, `category`, `created_at`

**Relationships**:
- `user_id` → `users.id` (Many-to-One)
- One-to-One with `conversations`
- One-to-One with `shared_comparisons`

#### 3. **shared_comparisons**
Stores publicly shareable comparisons.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID/String(36) | Primary key |
| `share_id` | String(8) | Unique share identifier |
| `comparison_id` | UUID/String(36) | FK to comparisons (nullable) |
| `user_id` | UUID/String(36) | FK to users (nullable) |
| `category` | String(100) | Comparison category |
| `items` | JSON | Array of items |
| `result` | JSON | Comparison result |
| `views` | Integer | View count |
| `expires_at` | DateTime | Expiration date (nullable) |
| `created_at` | DateTime | Share timestamp |

**Indexes**: `share_id` (unique), `created_at`, `expires_at`

**Relationships**:
- `comparison_id` → `comparisons.id` (One-to-One, nullable)
- `user_id` → `users.id` (Many-to-One, nullable)

#### 4. **conversations**
Stores follow-up conversation history.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID/String(36) | Primary key |
| `comparison_id` | UUID/String(36) | FK to comparisons |
| `user_id` | UUID/String(36) | FK to users (nullable) |
| `messages` | JSON | Array of chat messages |
| `original_comparison` | JSON | Snapshot of comparison |
| `items` | JSON | Items that were compared |
| `category` | String(100) | Comparison category |
| `created_at` | DateTime | Conversation start |
| `updated_at` | DateTime | Last message timestamp |

**Indexes**: `comparison_id`, `user_id`, `created_at`

**Relationships**:
- `comparison_id` → `comparisons.id` (One-to-One)
- `user_id` → `users.id` (Many-to-One, nullable)

#### 5. **comparison_cache**
Caches comparison results to reduce API calls.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID/String(36) | Primary key |
| `category` | String(100) | Comparison category |
| `items` | JSON | Normalized items array |
| `user_preferences` | JSON | User preferences JSON |
| `result` | JSON | Cached comparison result |
| `created_at` | DateTime | Cache creation time |
| `expires_at` | DateTime | Cache expiration time |

**Indexes**: `category`, `expires_at`

**Cache Lookup Logic**:
- For PostgreSQL: Fetches by category and filters in Python (JSON comparison complexity)
- For SQLite: Direct JSON comparison
- Default TTL: 24 hours

#### 6. **items**
Tracks popular items and comparison statistics.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID/String(36) | Primary key |
| `name` | String(255) | Item name (unique) |
| `category` | String(100) | Item category |
| `item_metadata` | JSON | Additional metadata |
| `comparison_count` | Integer | Times compared |
| `created_at` | DateTime | First comparison |
| `updated_at` | DateTime | Last comparison |

**Indexes**: `name` (unique), `category`

### Database Design Decisions

1. **UUID vs Auto-increment**: Uses String(36) UUIDs for better PostgreSQL/SQLite compatibility
2. **JSON Columns**: Flexible storage for dynamic data (comparison results, preferences)
3. **Nullable Foreign Keys**: Allows anonymous comparisons and sharing
4. **Cascade Deletes**: User deletion cascades to comparisons and conversations
5. **Indexes**: Strategic indexes on frequently queried columns
6. **Timestamps**: Automatic tracking of creation and updates

---

## 📁 Project Structure

```
COMPAIR/
├── backend/
│   ├── main.py                      # FastAPI application entry point
│   ├── requirements.txt             # Python dependencies
│   ├── prompt/
│   │   ├── __init__.py
│   │   └── prompt.py                # LLM prompt templates
│   ├── models/
│   │   ├── __init__.py
│   │   └── model.py                 # Pydantic models
│   ├── utilities/
│   │   ├── __init__.py
│   │   ├── constants.py             # Configuration constants
│   │   └── storage.py               # Data access layer
│   └── database/
│       ├── __init__.py
│       ├── models.py                # SQLAlchemy ORM models
│       ├── connection.py            # DB connection management
│       ├── repository.py            # CRUD operations
│       └── init_db.py               # Database initialization
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/              # React components
│   │   ├── pages/                   # Page components
│   │   ├── config/
│   │   │   └── api.js               # API configuration
│   │   └── App.js
│   ├── package.json
│   ├── Dockerfile                   # Frontend Docker image
│   └── nginx.conf                   # Nginx configuration
├── Dockerfile                        # Backend Docker image
├── docker-compose.yml               # Multi-service orchestration
├── .dockerignore
├── .env                             # Environment variables
├── docs/
│   ├── QUICK_REFERENCE.md           # Quick reference guide (start here!)
│   ├── OPTIMIZATION_SUMMARY.md      # Applied optimizations summary
│   ├── POSTGRESQL_AUDIT.md          # PostgreSQL audit & optimization guide
│   ├── SCALABILITY_ANALYSIS.md      # Scalability assessment & roadmap
│   ├── DATABASE_USECASES.md         # Database use cases documentation
│   ├── DATABASE_IMPLEMENTATION.MD   # Implementation details
│   └── DOCKER_SETUP.md              # Docker setup guide
├── backend/alembic/                  # Database migrations
│   └── versions/                    # Migration files
└── README.md                        # This file
```

---

## 🔌 API Documentation

### Base URL
```
Development: http://localhost:8000
Production: Configure via environment
```

### Endpoints

#### 1. Root
```http
GET /
```
Returns API welcome message.

#### 2. Health Check
```http
GET /health
```
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-01T19:43:28.538830",
  "version": "1.0.0"
}
```

#### 3. Database Health Check
```http
GET /health/db
```
**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "pool_size": 20,
  "checked_in_connections": 19,
  "checked_out_connections": 1,
  "overflow": -19,
  "timestamp": "2025-11-01T19:43:28.574720"
}
```
Returns database connection status and connection pool statistics.

#### 4. Compare Items
```http
POST /compare
```

**Request Body**:
```json
{
  "category": "Gadgets",
  "items": ["iPhone 15 Pro", "Samsung S24 Ultra"],
  "criteria": null,
  "user_preferences": {
    "priorities": ["camera", "battery life"],
    "budget": "$1000-1500",
    "use_case": "Photography and daily use"
  }
}
```

**Response**:
```json
{
  "comparison_id": "uuid",
  "category": "Gadgets",
  "items": ["iPhone 15 Pro", "Samsung S24 Ultra"],
  "introduction": "Let's compare...",
  "table": [
    {
      "feature": "Price",
      "iPhone 15 Pro": "$999",
      "Samsung S24 Ultra": "$1199"
    }
  ],
  "pros": [
    "iPhone 15 Pro: Excellent camera system",
    "Samsung S24 Ultra: Superior battery life"
  ],
  "cons": [
    "iPhone 15 Pro: Limited customization",
    "Samsung S24 Ultra: Higher price"
  ],
  "recommendation": "Based on your needs...",
  "personalized_winner": "iPhone 15 Pro",
  "winner_reason": "Given your priority for camera quality...",
  "message": null
}
```

#### 5. Save Comparison
```http
POST /save-comparison
```

**Request Body**:
```json
{
  "user_id": "user-uuid",
  "category": "Gadgets",
  "items": ["item1", "item2"],
  "result": { /* comparison result */ }
}
```

#### 6. Get History
```http
GET /history/{user_id}?limit=20&offset=0&category=Gadgets
```

#### 7. Delete History Item
```http
DELETE /delete-history-item/{user_id}/{comparison_id}
```

#### 8. Share Comparison
```http
POST /share-comparison
```

#### 9. Get Shared Comparison
```http
GET /get-shared-comparison/{share_id}
```

#### 10. Ask Follow-up Question
```http
POST /ask-followup
```

**Request Body**:
```json
{
  "comparison_id": "uuid",
  "question": "Which has better battery life?"
}
```

#### 11. Analytics Endpoints

**Trending Shared Comparisons**:
```http
GET /analytics/trending?days=7&limit=10
```

**Popular Items**:
```http
GET /analytics/popular-items?limit=10
```

**Category Statistics**:
```http
GET /analytics/category-stats
```

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)

### Quick Start with Docker

1. **Clone the repository**:
```bash
git clone https://github.com/wardacoder/COMPAIR.git
cd COMPAIR
```

2. **Set up environment variables**:
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY (required)
# - BRAVE_API_KEY (required)
# - Other variables are optional (defaults are provided)
```

3. **Start all services**:
```bash
docker-compose up --build
```

4. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export BRAVE_API_KEY="your-key"
export DATABASE_URL="postgresql://compair_user:compair_password@localhost:5432/compair_db"

# Initialize database
python database/init_db.py

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set API URL
export REACT_APP_API_URL="http://localhost:8000"

# Run development server
npm start
```

---

## 🔐 Environment Variables

All configuration is centralized in the `.env` file. 

### Quick Setup

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** and update the required values:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `BRAVE_API_KEY` - Your Brave Search API key

3. **Optional**: Adjust other settings as needed (defaults work for most cases)

### Required Variables

- **`OPENAI_API_KEY`**: Your OpenAI API key (get from https://platform.openai.com/account/api-keys)
- **`BRAVE_API_KEY`**: Your Brave Search API key (get from https://api.search.brave.com/)

### Optional Configuration Variables

See `.env.example` for a complete list of all available environment variables, including:

- **Brave Search Configuration**: `BRAVE_SEARCH_COUNT`, `BRAVE_SEARCH_SNIPPETS`, `BRAVE_SEARCH_TIMEOUT`
- **Database Configuration**: PostgreSQL credentials and connection settings
- **Port Mappings**: Customize ports for services
- **Container Names**: Customize Docker container names
- **Application Settings**: Backend and frontend configuration

### Environment Files

- **`.env.example`**: Template file with all available variables and documentation (committed to git)
- **`.env`**: Your actual configuration file (git-ignored, do NOT commit)

---

## 🐳 Docker Deployment

### Services

The application uses Docker Compose to orchestrate three services:

1. **PostgreSQL** (`postgres`):
   - Image: `postgres:15-alpine`
   - Port: 5432
   - Volume: `postgres_data` (persistent storage)
   - Health check: `pg_isready`

2. **Backend** (`backend`):
   - Build: `backend/Dockerfile`
   - Port: 8000
   - Environment: DATABASE_URL, OPENAI_API_KEY
   - Depends on: postgres (healthy)
   - Restart policy: always

3. **Frontend** (`frontend`):
   - Build: `frontend/Dockerfile` (multi-stage)
   - Port: 3000 → 80
   - Depends on: backend
   - Restart policy: always

### Docker Compose Commands

```bash
# Start all services
docker compose up -d

# Build and start
docker compose up --build -d

# View logs
docker compose logs -f [service-name]

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Restart a service
docker compose restart backend

# Execute command in service
docker compose exec backend python database/init_db.py
```

### Production Considerations

1. **Environment Variables**: Use secrets management (e.g., Docker secrets, Kubernetes secrets)
2. **SSL/TLS**: Add reverse proxy (Nginx/Traefik) with SSL certificates
3. **Monitoring**: Implement logging and monitoring (Prometheus, Grafana)
4. **Scaling**: Use orchestration platform (Kubernetes, Docker Swarm)
5. **API Rate Limiting**: Implement rate limiting for API endpoints
6. **CDN**: Serve frontend assets via CDN

---

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.10+
- **LLM**: OpenAI GPT-4o via LangChain
- **ORM**: SQLAlchemy 2.0.35
- **Database Driver**: psycopg2-binary 2.9.10
- **Validation**: Pydantic 2.x
- **ASGI Server**: Uvicorn

### Frontend
- **Framework**: React 18
- **Build Tool**: Create React App
- **HTTP Client**: Fetch API
- **Web Server**: Nginx (Alpine)

### Database
- **Primary**: PostgreSQL 15 (Alpine) - **Optimized** ⚡
- **Alternative**: SQLite 3 (for development)
- **Data Format**: JSONB for all JSON columns (2-3x faster)
- **Connection Pool**: 20 connections + 10 overflow (optimized)
- **Schema**: 6 tables, 23 indexes (3 composite), proper foreign keys
- **Migrations**: Alembic for version control

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose

---

## 📊 Performance & Scalability

### Current Performance Optimizations ⚡

1. **JSONB Storage**: All JSON columns use PostgreSQL JSONB (2-3x faster)
2. **Connection Pool**: 20 persistent + 10 overflow connections (optimized)
3. **Database Tuning**: PostgreSQL configured for 2GB RAM, SSD storage
4. **Composite Indexes**: 3 composite indexes for common query patterns
5. **Query Optimization**: Eager loading to prevent N+1 queries
6. **Caching**: 24-hour cache for comparison results in JSONB
7. **Strategic Indexing**: 23 indexes on frequently queried columns
8. **Static File Serving**: Nginx for frontend assets
9. **Health Monitoring**: `/health` and `/health/db` endpoints

---

## 🛠️ Development Guidelines

### Code Organization
- **Backend**: Modular structure with separation of concerns
- **Frontend**: Component-based architecture
- **Database**: Repository pattern for data access

### Best Practices
- Type hints for Python code
- Pydantic validation for API requests/responses
- Error handling and logging
- Database transactions for data integrity
- Environment-based configuration

---

## 🔄 Version History

- **v1.0.0** (2025-11-01): Initial release
  - AI-powered comparisons
  - User history and sharing
  - PostgreSQL integration
  - Docker deployment
  - Analytics endpoints

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- FastAPI framework
- React community
- LangChain project
