# Database Use Cases for Compair Project

## Current Storage Implementation
The project currently uses:
- **JSON files** for persistent storage (`comparison_history.json`, `shared_comparisons.json`)
- **In-memory dictionary** (`conversation_memory`) for temporary conversation follow-ups

## Database Use Cases

### 1. **User Comparison History** 
**Current Implementation:** JSON file with user_id as keys
**Database Benefits:**
- **Efficient queries**: Query by user_id, date range, category, items
- **Pagination**: Fetch history with limit/offset for large datasets
- **Indexing**: Fast lookups with database indexes
- **Scalability**: Handle thousands of users without loading entire file
- **Data integrity**: Foreign key constraints and validation

**Example Queries:**
```sql
-- Get recent comparisons for a user
SELECT * FROM comparisons 
WHERE user_id = ? 
ORDER BY created_at DESC 
LIMIT 20 OFFSET 0;

-- Get comparisons by category
SELECT * FROM comparisons 
WHERE user_id = ? AND category = ?
ORDER BY created_at DESC;

-- Search comparisons by items
SELECT * FROM comparisons 
WHERE user_id = ? AND items LIKE '%iPhone%';
```

### 2. **Shared Comparisons**
**Current Implementation:** JSON file with share_id as keys
**Database Benefits:**
- **View tracking**: Efficiently track and update view counts
- **Expiration**: Auto-expire shared links after X days
- **Analytics**: Track popular shared comparisons
- **Concurrent access**: Handle multiple simultaneous view requests safely
- **Metadata**: Store expiration dates, access control, privacy settings

**Example Queries:**
```sql
-- Increment view count atomically
UPDATE shared_comparisons 
SET views = views + 1 
WHERE share_id = ?;

-- Get trending shared comparisons
SELECT * FROM shared_comparisons 
WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY views DESC 
LIMIT 10;

-- Clean up expired shares
DELETE FROM shared_comparisons 
WHERE expires_at < NOW();
```

### 3. **Conversation Follow-ups (Persistent Storage)**
**Current Implementation:** In-memory dictionary (lost on server restart)
**Database Benefits:**
- **Persistence**: Conversation history survives server restarts
- **Long-term storage**: Store conversations for future reference
- **User retrieval**: Users can access their conversation history later
- **Analytics**: Analyze common follow-up questions
- **Session management**: Track conversation sessions with timestamps

**Example Schema:**
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    comparison_id UUID NOT NULL,
    user_id VARCHAR(255),
    messages JSONB, -- Store array of messages
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 4. **User Management & Authentication**
**Current Implementation:** No user system (using user_id strings)
**Database Benefits:**
- **User accounts**: Store user profiles, preferences, settings
- **Authentication**: Secure password storage and session management
- **User preferences**: Store default preferences per user
- **Usage analytics**: Track user activity and engagement

**Example Schema:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(255),
    created_at TIMESTAMP,
    preferences JSONB -- Store UserPreferences
);
```

### 5. **Comparison Analytics & Insights**
**Database Benefits:**
- **Popular comparisons**: Track most compared items
- **Category trends**: See trending categories over time
- **Item popularity**: Track which items are compared most
- **User behavior**: Analyze comparison patterns
- **Performance metrics**: Track API response times, success rates

**Example Queries:**
```sql
-- Most compared items
SELECT items, COUNT(*) as comparison_count
FROM comparisons
GROUP BY items
ORDER BY comparison_count DESC
LIMIT 10;

-- Category popularity over time
SELECT category, DATE(created_at) as date, COUNT(*) as count
FROM comparisons
GROUP BY category, DATE(created_at)
ORDER BY date DESC;
```

### 6. **Caching & Performance**
**Database Benefits:**
- **Query caching**: Cache frequently accessed comparisons
- **Duplicate detection**: Detect and cache identical comparison requests
- **Response caching**: Store LLM responses for identical queries
- **Rate limiting**: Track API usage per user/IP

**Example Use Case:**
```sql
-- Check if comparison already exists
SELECT result FROM comparison_cache
WHERE category = ? 
AND items = ?
AND user_preferences = ?
LIMIT 1;
```

### 7. **Data Relationships & Normalization**
**Database Benefits:**
- **Normalized data**: Separate tables for items, categories, comparisons
- **Referential integrity**: Ensure data consistency
- **Efficient updates**: Update item details in one place
- **Complex queries**: Join related data efficiently

**Example Schema:**
```sql
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    category VARCHAR(100),
    metadata JSONB
);

CREATE TABLE comparisons (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    category VARCHAR(100),
    created_at TIMESTAMP,
    result JSONB
);

CREATE TABLE comparison_items (
    comparison_id UUID REFERENCES comparisons(id),
    item_id INTEGER REFERENCES items(id),
    PRIMARY KEY (comparison_id, item_id)
);
```

## Recommended Database Choice

### **PostgreSQL** (Recommended)
- **Why**: Best for structured data with relationships
- **Features**: JSONB support, full-text search, excellent performance
- **Use cases**: All of the above

### **SQLite** (Development/Simple)
- **Why**: Easy setup, no server needed, file-based
- **Features**: Good for smaller applications
- **Limitations**: Not ideal for high concurrency

### **MongoDB** (Alternative)
- **Why**: Good for flexible JSON-like data structures
- **Features**: Easy schema evolution, document-based
- **Use cases**: Good if you want to keep JSON-like structure

## Migration Strategy

1. **Phase 1**: Migrate shared comparisons (least critical)
2. **Phase 2**: Migrate user history (medium priority)
3. **Phase 3**: Add persistent conversation storage
4. **Phase 4**: Add user authentication system
5. **Phase 5**: Add analytics and caching

## Benefits Summary

| Current (JSON Files) | With Database |
|---------------------|---------------|
| Load entire file for any query | Query specific data |
| No concurrent write safety | ACID transactions |
| Data lost on restart (conversations) | Persistent storage |
| Limited query capabilities | Complex queries & joins |
| Hard to scale | Handles millions of records |
| No relationships | Enforced relationships |
| No user management | Full user system |
| No analytics | Rich analytics & insights |

