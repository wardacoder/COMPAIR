# Feedback System Data Flow

## Overview
The feedback system allows users to rate comparisons (1-5 stars) and provide optional text comments. The system processes this feedback to generate analytics for the dashboard and MCP tools.

---

## 1. Feedback Submission Flow

### Input: User Submits Feedback
```
Frontend → POST /feedback
Request Body (FeedbackRequest):
{
  "comparison_id": "uuid-string",    // Links to Comparison.comparison_id
  "rating": 1-5,                     // Star rating (required)
  "comment": "optional text",         // Optional structured text
  "user_id": "optional"               // Optional (not currently used)
}
```

### Processing Steps

**Step 1: API Endpoint Receives Request**
- **Location**: `backend/main.py` → `submit_feedback()`
- **Action**: Validates request using `FeedbackRequest` Pydantic model
- **Validation**: Ensures rating is between 1-5

**Step 2: Database Session Creation**
- **Location**: `database/connection.py` → `get_db_session()`
- **Action**: Creates database session context manager
- **Database**: PostgreSQL (JSONB) or SQLite (JSON fallback)

**Step 3: Create Feedback Record**
- **Location**: `database/repository.py` → `create_feedback()`
- **Action**: 
  - Creates new `Feedback` model instance
  - Sets `comparison_id`, `rating`, `comment`
  - Auto-generates `id` (UUID) and `created_at` timestamp
  - Commits to database

**Step 4: Database Storage**
- **Table**: `feedback`
- **Schema**:
  ```sql
  id: UUID (Primary Key)
  comparison_id: String(36) (Indexed, references Comparison.comparison_id)
  rating: Integer (1-5)
  comment: Text (nullable)
  created_at: DateTime (Indexed)
  updated_at: DateTime
  ```
- **Indexes**: 
  - `ix_feedback_comparison_created` on (comparison_id, created_at)

**Step 5: Response**
- **Returns**: 
  ```json
  {
    "message": "Feedback submitted successfully",
    "feedback_id": "uuid",
    "rating": 5
  }
  ```

---

## 2. Feedback Retrieval Flow

### Get Feedback for a Comparison
```
Frontend → GET /feedback/{comparison_id}
```

**Processing**:
1. **Endpoint**: `backend/main.py` → `get_feedback()`
2. **Repository**: `database/repository.py` → `get_feedback_by_comparison()`
3. **Query**: Filters `Feedback` table by `comparison_id`, ordered by `created_at DESC`
4. **Returns**: List of all feedback entries for that comparison

---

## 3. Feedback Analytics Processing Flow

### Aggregate Statistics Endpoint
```
Frontend/Dashboard → GET /analytics/feedback-stats?days=30
```

### Processing Pipeline

**Step 1: Fetch Feedback Data**
- **Location**: `database/repository.py` → `get_feedback_stats()`
- **Query**: Retrieves all `Feedback` records within date range (default: 30 days)
- **Filter**: `Feedback.created_at >= cutoff_date`

**Step 2: Calculate Basic Metrics**

**A. Comprehensiveness Score**
- **Calculation**: `sum(all ratings) / total_feedback_count`
- **Output**: Average rating (0.0 - 5.0)
- **Use**: Overall quality metric

**B. Rating Breakdown**
- **Calculation**: Count feedback by rating (1★, 2★, 3★, 4★, 5★)
- **Output**: `{"1": count, "2": count, ..., "5": count}`
- **Use**: Star distribution chart

**Step 3: Parse Structured Comments**

The `comment` field contains structured text separated by `" | "` delimiter:

**Comment Format Examples**:
```
"Decision help: Yes, I know what to choose | Winner match: 4/5 | Liked: \"Great detail\" | Improvement: \"More examples\""
```

**Parsing Logic**:

**A. Decision Helpfulness**
- **Pattern**: `"Decision help: <text>"`
- **Extracts**:
  - `"Yes, I know what to choose"` → `yes_decided++`
  - `"Somewhat"` → `somewhat++`
  - `"No, still confused"` → `still_confused++`
  - Contains `"different"` → `need_different++`
- **Output**: Counts for each decision category

**B. Winner Match Score**
- **Pattern**: `"Winner match: <rating>/5"`
- **Extracts**: Rating value (1-5)
- **Calculation**: Average of all winner match ratings
- **Output**: Score (0.0 - 5.0) and count
- **Use**: Measures how well AI-picked winners match user needs

**C. Liked Comments**
- **Pattern**: `"Liked: \"<text>\""`
- **Extracts**: Text content (removes quotes)
- **Filters**: Empty strings and placeholder values
- **Output**: Array of `{"text": "..."}` objects
- **Use**: Positive feedback themes

**D. Improvement Suggestions**
- **Pattern**: `"Improvement: \"<text>\""`
- **Extracts**: Text content (removes quotes)
- **Filters**: Empty strings and placeholder values
- **Output**: Array of `{"text": "..."}` objects
- **Additional Processing**: 
  - Counts occurrences of common phrases
  - Generates `top_improvements` (top 5 most frequent)
- **Use**: Areas needing improvement

**Step 4: Calculate Response Rate**
- **Query**: Count total `Comparison` records in date range
- **Calculation**: `(total_feedback / total_comparisons) * 100`
- **Output**: Percentage (capped at 100%)
- **Use**: Feedback engagement metric

**Step 5: Return Aggregated Statistics**
```json
{
  "total_feedback": 150,
  "comprehensiveness_score": 4.2,
  "rating_breakdown": {"1": 5, "2": 10, "3": 20, "4": 50, "5": 65},
  "decision_helpfulness": {
    "yes_decided": 80,
    "somewhat": 30,
    "still_confused": 20,
    "need_different": 20
  },
  "winner_match_score": 4.1,
  "winner_match_count": 100,
  "liked_comments": [{"text": "Great detail"}, ...],
  "improvement_comments": [{"text": "More examples"}, ...],
  "top_improvements": [
    {"text": "more examples", "count": 15},
    ...
  ],
  "feedback_response_rate": 25.5
}
```

---

## 4. Dashboard Integration Flow

### Dashboard Summary Endpoint
```
Frontend → GET /analytics/dashboard?days=30
```

**Processing**:
1. **Location**: `backend/main.py` → `get_dashboard()`
2. **Repository**: `database/repository.py` → `get_dashboard_summary()`
3. **Action**: Calls `get_feedback_stats()` and includes in summary
4. **Output**: Complete dashboard data including `feedback_stats` object

**Dashboard Data Structure**:
```json
{
  "total_comparisons": 500,
  "personalized_count": 300,
  "general_count": 200,
  "feedback_stats": {
    // ... full feedback statistics (see Step 5 above)
  },
  "category_stats": [...],
  "trends": [...],
  "winner_distribution": [...]
}
```

---

## 5. MCP Server Integration Flow

### MCP Tools Access Feedback Data
```
AI Assistant → POST /tools/invoke
{
  "tool_name": "get_comparison_quality" | "get_decision_confidence" | "get_user_feedback_summary"
}
```

**Processing**:
1. **Location**: `backend/mcp_server.py`
2. **Tools**:
   - `tool_get_comparison_quality()` → Uses `get_feedback_stats()` → Returns comprehensiveness metrics
   - `tool_get_decision_confidence()` → Uses `get_feedback_stats()` → Returns decision helpfulness + winner match
   - `tool_get_user_feedback_summary()` → Uses `get_feedback_stats()` → Returns liked/improvement comments
3. **Data Source**: Same `get_feedback_stats()` repository function
4. **Output**: Formatted for AI consumption with insights and assessments

---

## 6. Data Relationships

```
Comparison (comparisons table)
  ├── comparison_id (unique identifier)
  └── original_comparison (JSONB) - stores comparison result

Feedback (feedback table)
  ├── comparison_id → references Comparison.comparison_id
  ├── rating (1-5)
  └── comment (structured text with delimiters)
```

**Note**: `Feedback.comparison_id` references `Comparison.comparison_id` (not a foreign key constraint, but logical reference).

---

## 7. Key Data Transformations

### Comment Parsing Example
**Input Comment**:
```
"Decision help: Yes, I know what to choose | Winner match: 4/5 | Liked: \"Great detail\" | Improvement: \"More examples\""
```

**Parsed Output**:
- Decision: `yes_decided` count incremented
- Winner Match: Rating `4` added to array
- Liked: `{"text": "Great detail"}` added to array
- Improvement: `{"text": "More examples"}` added to array

### Aggregation Example
**Input**: 100 feedback records with ratings [5, 4, 5, 3, 5, ...]

**Output**:
- Comprehensiveness Score: `4.2` (average)
- Rating Breakdown: `{"5": 60, "4": 30, "3": 10, "2": 0, "1": 0}`

---

## 8. Performance Considerations

- **Indexes**: 
  - `comparison_id` indexed for fast lookups
  - Composite index on `(comparison_id, created_at)` for sorted queries
- **Caching**: None currently (could cache `get_feedback_stats()` results)
- **Query Optimization**: Single query fetches all feedback, then processes in Python (efficient for moderate data volumes)

---

## Summary Flow Diagram

```
[User] 
  ↓
[Frontend] POST /feedback {comparison_id, rating, comment}
  ↓
[Backend API] submit_feedback()
  ↓
[Repository] create_feedback()
  ↓
[Database] INSERT INTO feedback
  ↓
[Response] {feedback_id, rating}

---

[Analytics Request]
  ↓
[Backend API] GET /analytics/feedback-stats
  ↓
[Repository] get_feedback_stats()
  ↓
[Database] SELECT * FROM feedback WHERE created_at >= cutoff
  ↓
[Processing] Parse comments, calculate metrics
  ↓
[Response] Aggregated statistics

---

[Dashboard Request]
  ↓
[Backend API] GET /analytics/dashboard
  ↓
[Repository] get_dashboard_summary()
  ├─→ get_feedback_stats() (includes feedback data)
  └─→ Other analytics functions
  ↓
[Response] Complete dashboard data

---

[MCP Request]
  ↓
[MCP Server] POST /tools/invoke
  ↓
[Tool Function] (e.g., tool_get_comparison_quality)
  ↓
[Repository] get_feedback_stats()
  ↓
[Response] Formatted feedback insights
```

---

## Key Files Reference

- **API Endpoints**: `backend/main.py` (lines 1193-1300)
- **Repository Functions**: `backend/database/repository.py` (lines 393-550)
- **Data Models**: `backend/database/models.py` (lines 115-133)
- **Request Models**: `backend/models/model.py` (lines 94-100)
- **MCP Tools**: `backend/mcp_server.py` (lines 105-371)




