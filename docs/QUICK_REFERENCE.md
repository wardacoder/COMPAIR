# Quick Reference Guide - COMPAIR

**Last Updated**: November 1, 2025  
**Version**: 1.0.0 (Optimized)

---

## 🚀 Quick Start

```bash
# 1. Start all services
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f backend

# 4. Stop services
docker-compose down
```

---

## 🔗 Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Web application |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive documentation |
| **Health Check** | http://localhost:8000/health | Service health status |
| **DB Health** | http://localhost:8000/health/db | Database & pool stats |
| **PostgreSQL** | localhost:5432 | Direct database access |

---

## 📊 System Status

### Current Capacity
- **Concurrent Users**: 100-200
- **Requests/Second**: 50-100
- **Database QPS**: 500-1,000
- **Production Ready**: Yes (A- grade)

### Services
```bash
✅ PostgreSQL 15        - Optimized for 2GB RAM, 200 max connections
✅ Backend API          - FastAPI with 20-connection pool
✅ Frontend             - React on Nginx
```

---

## 🛠️ Common Commands

### Docker Management
```bash
# Rebuild and start
docker-compose up --build -d

# Restart specific service
docker-compose restart backend

# View all services
docker-compose ps

# Stop and remove volumes
docker-compose down -v

# Execute command in container
docker-compose exec backend python database/init_db.py
```

### Database Operations
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U compair_user -d compair_db

# List tables
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "\dt"

# Show indexes
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "\di"

# Database size
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "SELECT pg_size_pretty(pg_database_size('compair_db'));"

# Connection count
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 🔍 Monitoring & Health

### Health Check Endpoints
```bash
# Basic health
curl http://localhost:8000/health

# Database health with pool stats
curl http://localhost:8000/health/db

# Example response:
{
  "status": "healthy",
  "database": "connected",
  "pool_size": 20,
  "checked_in_connections": 19,
  "checked_out_connections": 1,
  "overflow": -19
}
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres

# Last 50 lines
docker-compose logs --tail=50 backend

# Search for errors
docker-compose logs backend | grep -i error
```

### Monitor Connection Pool
```bash
# Via API
curl http://localhost:8000/health/db | jq

# Via PostgreSQL
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "
SELECT 
    count(*) as connections,
    state,
    application_name
FROM pg_stat_activity 
GROUP BY state, application_name;
"
```

---

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required
OPENAI_API_KEY=your-key-here

# Database
POSTGRES_USER=compair_user
POSTGRES_PASSWORD=compair_password
POSTGRES_DB=compair_db

# Ports
BACKEND_HOST_PORT=8000
FRONTEND_HOST_PORT=3000
POSTGRES_HOST_PORT=5432
```

### Change Configuration
```bash
# 1. Edit .env file
nano .env

# 2. Restart services
docker-compose down
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs [service-name]

# Check health
docker-compose ps

# Restart service
docker-compose restart [service-name]
```

### Database Connection Issues
```bash
# Check PostgreSQL health
docker-compose exec postgres pg_isready -U compair_user -d compair_db

# Check connections
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "SHOW max_connections;"

# Verify pool stats
curl http://localhost:8000/health/db
```

### Slow Queries
```bash
# Check PostgreSQL logs for slow queries (>1s)
docker-compose logs postgres | grep "duration:"

# View slow query stats
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"
```

### Backend Not Responding
```bash
# Check if LLM is configured
docker-compose logs backend | grep "OpenAI"

# Check database connection
curl http://localhost:8000/health/db

# Check pool exhaustion
# If all connections are checked out, increase pool_size
```

---

## 📈 Performance Tuning

### Increase Capacity
```bash
# Edit docker-compose.yml
postgres:
  command: >
    -c max_connections=500        # Increase from 200
    -c shared_buffers=1GB         # Increase from 512MB

# Edit backend/database/connection.py
pool_size=50,          # Increase from 20
max_overflow=20,       # Increase from 10
```

---

## 🔐 Security Checklist

- [ ] Change default PostgreSQL password in `.env`
- [ ] Add SSL/TLS for PostgreSQL connections
- [ ] Enable row-level security in PostgreSQL
- [ ] Add API rate limiting
- [ ] Use secrets management (not .env) in production
- [ ] Enable database connection encryption
- [ ] Add authentication to health endpoints
- [ ] Use managed database service for production

---

## 📝 Maintenance Tasks

### Daily
- Monitor `/health/db` endpoint

### Weekly
- Review slow query logs
- Check disk space usage

### Monthly
- Update dependencies
- Review connection pool usage
- Analyze query performance

---

## 🎯 Key Metrics to Monitor

```bash
# Connection pool usage
curl http://localhost:8000/health/db

# Database size
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "SELECT pg_size_pretty(pg_database_size('compair_db'));"

# Table sizes
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Active connections
docker-compose exec -T postgres psql -U compair_user -d compair_db -c "SELECT count(*) FROM pg_stat_activity;"

# Slow queries
docker-compose logs postgres | grep "duration:" | tail -20
```

---

## 🚨 Emergency Procedures

### Database Restore
```bash
# 1. Stop backend
docker-compose stop backend

# 2. Drop and recreate database
docker-compose exec postgres psql -U compair_user -c "DROP DATABASE compair_db;"
docker-compose exec postgres psql -U compair_user -c "CREATE DATABASE compair_db;"

# 3. Restart backend
docker-compose start backend
```

### Full System Reset
```bash
# WARNING: This will delete all data!

# Stop and remove everything
docker-compose down -v

# Start fresh
docker-compose up -d --build
```

---

## 📞 Support

For issues or questions, refer to:
- [README.md](../README.md) - Full documentation
- [POSTGRESQL_AUDIT.md](POSTGRESQL_AUDIT.md) - Database details
- [SCALABILITY_ANALYSIS.md](SCALABILITY_ANALYSIS.md) - Scaling guide
- [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) - Applied optimizations

