# COMPAIR Setup Guide - Complete Installation

This guide will help you set up COMPAIR with all three new features: Dashboard, Feedback, and MCP integration.

## Prerequisites

- Docker & Docker Compose (recommended) OR
- Python 3.9+, Node.js 16+, PostgreSQL 15+
- OpenAI API Key
- Brave Search API Key (optional)

## Quick Start (Docker - Recommended)

### 1. Clone and Configure

```bash
# Clone the repository
cd COMPAIR

# Create .env file
cp .env.example .env  # or create manually
```

### 2. Configure Environment Variables

Edit `.env` file:

```env
# Database
POSTGRES_USER=compair
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=compair_db
POSTGRES_CONTAINER_NAME=compair-postgres
POSTGRES_HOST_PORT=5432
POSTGRES_PORT=5432
DATABASE_URL=postgresql://compair:your_secure_password@postgres:5432/compair_db

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
BRAVE_API_KEY=your_brave_api_key_here

# Backend
BACKEND_CONTAINER_NAME=compair-backend
BACKEND_HOST=0.0.0.0
BACKEND_CONTAINER_PORT=8000
BACKEND_HOST_PORT=8000
BACKEND_RELOAD=--reload

# Frontend
FRONTEND_CONTAINER_NAME=compair-frontend
FRONTEND_CONTAINER_PORT=80
FRONTEND_HOST_PORT=3000
REACT_APP_API_URL=http://localhost:8000

# MCP Server
MCP_CONTAINER_NAME=compair-mcp
MCP_HOST=0.0.0.0
MCP_PORT=8001
MCP_HOST_PORT=8001
```

### 3. Update Docker Compose

Add MCP service to `docker-compose.yml`:

```yaml
  mcp:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ${MCP_CONTAINER_NAME}
    environment:
      DATABASE_URL: ${DATABASE_URL}
      MCP_HOST: ${MCP_HOST}
      MCP_PORT: ${MCP_PORT}
    ports:
      - "${MCP_HOST_PORT}:${MCP_PORT}"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: python mcp_server.py
    restart: always
```

### 4. Start All Services

```bash
# Build and start all containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Verify Services

```bash
# Backend API
curl http://localhost:8000/health

# MCP Server
curl http://localhost:8001/health

# Frontend
open http://localhost:3000
```

### 6. Initialize Database

The database is automatically initialized on first run. If you need to re-initialize:

```bash
docker-compose exec backend python database/init_db.py
```

## Manual Setup (Without Docker)

### 1. Setup PostgreSQL

```bash
# Install PostgreSQL
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-15

# Create database
psql postgres
CREATE DATABASE compair_db;
CREATE USER compair WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE compair_db TO compair;
\q
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://compair:your_password@localhost:5432/compair_db
OPENAI_API_KEY=your_openai_api_key
BRAVE_API_KEY=your_brave_api_key
EOF

# Initialize database
python database/init_db.py

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Setup MCP Server (New Terminal)

```bash
cd backend
source venv/bin/activate  # Use same virtual environment

# Start MCP server
python mcp_server.py

# Or specify port
MCP_PORT=8001 python mcp_server.py
```

### 4. Setup Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start development server
npm start
```

### 5. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MCP Server**: http://localhost:8001
- **MCP Tools**: http://localhost:8001/tools

## Feature Configuration

### Dashboard

No additional configuration needed. Access at `/dashboard` route.

**Customization:**

Edit `frontend/src/pages/Dashboard.jsx`:
- Modify time ranges
- Add/remove metrics
- Customize chart colors

### Feedback System

No additional configuration needed. Automatically appears after comparisons.

**Customization:**

Edit `frontend/src/components/FeedbackSection.jsx`:
- Modify rating system (stars, thumbs, etc.)
- Add custom fields
- Change submission behavior

### MCP Server

**Basic Configuration:**

The MCP server is ready to use out of the box.

**ChatGPT Integration:**

1. **Create Custom GPT** (ChatGPT Plus required):
   - Go to https://chat.openai.com/gpts/editor
   - Click "Create a GPT"
   - Set name: "COMPAIR Assistant"

2. **Configure Instructions**:
```
You are a COMPAIR analytics assistant with access to comparison data.

Use these tools to help users:
- get_comparison_history: View user's past comparisons
- get_analytics_summary: Get overall platform statistics
- get_trending_items: See what's popular
- get_feedback_insights: Check user satisfaction
- get_winner_patterns: Analyze winning items
- get_category_insights: Category usage trends
- get_personalized_recommendations: Generate smart recommendations

Always provide context and explain your recommendations.
```

3. **Add Actions** (Configure API):
   - Schema: Import OpenAPI schema from http://localhost:8001/openapi.json
   - Authentication: None (or API Key for production)
   - Base URL: http://your-public-server:8001

4. **Test Integration**:
```
User: "What have I been comparing lately?"
GPT: *Uses get_comparison_history tool*
GPT: "Based on your recent activity, you've been primarily..."
```

## Production Deployment

### Security Hardening

1. **Environment Variables**:
```env
# Use strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Restrict CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Add API keys
MCP_API_KEY=$(openssl rand -hex 32)
```

2. **Update MCP Server** (`backend/mcp_server.py`):
```python
# Add authentication
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.getenv("MCP_API_KEY"):
        raise HTTPException(status_code=403)
    return api_key

# Restrict CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

3. **Use HTTPS**:
```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

### Database Optimization

```sql
-- Create additional indexes for performance
CREATE INDEX idx_feedback_rating ON feedback(rating);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);
CREATE INDEX idx_comparisons_created_at ON comparisons(created_at);

-- Analyze tables
ANALYZE comparisons;
ANALYZE feedback;
ANALYZE items;
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/compair

upstream backend {
    server localhost:8000;
}

upstream mcp {
    server localhost:8001;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /var/www/compair/frontend/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # MCP Server
    location /mcp {
        proxy_pass http://mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Database
curl http://localhost:8000/health/db

# MCP
curl http://localhost:8001/health
```

### Logs

```bash
# Docker
docker-compose logs -f backend
docker-compose logs -f mcp
docker-compose logs -f frontend

# Manual
tail -f backend/logs/app.log
tail -f backend/logs/mcp.log
```

### Metrics

Add monitoring with Prometheus and Grafana:

```yaml
# docker-compose.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
```

## Troubleshooting

### Issue: Database Connection Failed

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres  # Docker
pg_isready  # Manual

# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: MCP Server Not Starting

**Solution:**
```bash
# Check port availability
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Check logs
docker-compose logs mcp

# Test manually
cd backend
python mcp_server.py
```

### Issue: Frontend Can't Connect to Backend

**Solution:**
```bash
# Check REACT_APP_API_URL
cat frontend/.env

# Verify backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/main.py
```

### Issue: Feedback Not Saving

**Solution:**
```bash
# Check feedback table exists
docker-compose exec postgres psql -U compair -d compair_db -c "\dt feedback"

# Re-run migrations
docker-compose exec backend python database/init_db.py

# Check logs
docker-compose logs backend | grep feedback
```

### Issue: Dashboard Shows No Data

**Solution:**
```bash
# Check if data exists
docker-compose exec postgres psql -U compair -d compair_db -c "SELECT COUNT(*) FROM comparisons"

# Verify analytics endpoint
curl http://localhost:8000/analytics/dashboard?days=90

# Check time range filter
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/

# Specific test
pytest tests/test_feedback.py

# With coverage
pytest --cov=. tests/
```

### Frontend Tests

```bash
cd frontend
npm test

# Coverage
npm test -- --coverage
```

### MCP Server Tests

```bash
# Test tool listing
curl http://localhost:8001/tools

# Test tool invocation
curl -X POST http://localhost:8001/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_analytics_summary",
    "parameters": {"days": 7}
  }'
```

## Backup & Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U compair compair_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U compair compair_db < backup.sql
```

### Full Backup

```bash
# Backup everything
tar -czf compair-backup-$(date +%Y%m%d).tar.gz \
  backend/ \
  frontend/ \
  data/ \
  docker-compose.yml \
  .env
```

## Updating

### Pull Latest Changes

```bash
git pull origin main

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run migrations
docker-compose exec backend python database/init_db.py
```

## Support

- **Documentation**: See `/docs` folder
- **Issues**: Check existing issues or create new one
- **API Docs**: http://localhost:8000/docs
- **MCP Docs**: [MCP_INTEGRATION.md](./MCP_INTEGRATION.md)
- **Features**: [FEATURES_OVERVIEW.md](./FEATURES_OVERVIEW.md)

## Next Steps

1. ✅ Complete setup and verify all services are running
2. 📊 Explore the Dashboard at `/dashboard`
3. ⭐ Try submitting feedback on a comparison
4. 🤖 Configure ChatGPT integration with MCP server
5. 📈 Monitor usage and analytics
6. 🚀 Deploy to production

---

**Congratulations!** 🎉 You now have a fully functional COMPAIR system with visual analytics, user feedback, and intelligent AI integration!

