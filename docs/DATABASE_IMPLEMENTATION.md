# Database Implementation Guide

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Configuration

The application uses SQLite by default (for development). To use PostgreSQL:

Set environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/compair"
```

Or add to `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost:5432/compair
```

### 3. Initialize Database

Run the initialization script:
```bash
python backend/database/init_db.py
```

This will create all necessary tables.

### 4. Database Schema

The database includes the following tables:

- **users**: User accounts and preferences
- **comparisons**: User comparison history
- **shared_comparisons**: Publicly shared comparisons
- **conversations**: Follow-up conversation history
- **comparison_cache**: Cached comparison results
- **items**: Popular items tracking

### 5. Features Implemented

✅ **User Comparison History**
- Store and retrieve user comparisons
- Pagination support (limit/offset)
- Category filtering
- Search by items

✅ **Shared Comparisons**
- Share comparisons with unique IDs
- View tracking (atomic increments)
- Expiration support
- Trending comparisons

✅ **Persistent Conversation Storage**
- Store follow-up conversations in database
- Retrieve conversation history
- Message tracking with timestamps

✅ **Caching System**
- Cache comparison results
- Reduce LLM API calls
- Automatic expiration

✅ **Analytics**
- Trending shared comparisons
- Most compared items
- Category statistics

✅ **Item Tracking**
- Track popular items
- Comparison count per item

### 6. API Endpoints

All existing endpoints work with database:
- `POST /compare` - Now includes caching
- `POST /save-comparison` - Saves to database
- `GET /history/{user_id}` - With pagination support
- `POST /share-comparison` - Creates database entry
- `GET /shared/{share_id}` - With view tracking
- `POST /ask-followup` - Stores in database
- `GET /followup-history/{comparison_id}` - Retrieves from database
- `DELETE /history/{user_id}/{comparison_id}` - Database deletion

New Analytics Endpoints:
- `GET /analytics/trending` - Trending shared comparisons
- `GET /analytics/popular-items` - Most compared items
- `GET /analytics/category-stats` - Category statistics

### 7. Migration from JSON Files

The old JSON file storage has been completely replaced. The database will:
- Automatically create users when they save comparisons
- Handle all data persistence
- Support concurrent access safely

### 8. Maintenance

Cleanup expired data:
```python
from database.connection import get_db_session
from database.repository import cleanup_expired_shares, cleanup_expired_cache

with get_db_session() as db:
    cleanup_expired_shares(db)
    cleanup_expired_cache(db)
```

### 9. Production Considerations

For production, consider:
- Using PostgreSQL instead of SQLite
- Setting up database backups
- Schema version control for production environments
- Implementing connection pooling
- Adding database indexes for performance
- Setting up monitoring and logging

