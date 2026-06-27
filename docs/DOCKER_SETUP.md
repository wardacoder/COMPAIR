# Docker Setup Guide

## Quick Start

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

2. **Build and start services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the API:**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Services

### PostgreSQL Database
- **Container**: `compair_postgres`
- **Port**: 5432
- **Database**: `compair_db`
- **User**: `compair_user`
- **Password**: `compair_password`
- **Data**: Persisted in `postgres_data` volume

### Backend API
- **Container**: `compair_backend`
- **Port**: 8000
- **Auto-reload**: Enabled for development
- **Dependencies**: Waits for PostgreSQL to be healthy before starting

## Commands

### Start services
```bash
docker-compose up
```

### Start in background
```bash
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (clears database)
```bash
docker-compose down -v
```

### Rebuild after code changes
```bash
docker-compose up --build
```

### Execute commands in backend container
```bash
docker-compose exec backend python database/init_db.py
docker-compose exec backend python -m pytest
```

### Access PostgreSQL shell
```bash
docker-compose exec postgres psql -U compair_user -d compair_db
```

## Environment Variables

Create a `.env` file in the project root with:

```env
OPENAI_API_KEY=your_key_here
```

The `DATABASE_URL` is automatically set by docker-compose and connects to the PostgreSQL service.

## Troubleshooting

### Database connection issues
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check logs: `docker-compose logs postgres`
- Wait a few seconds for PostgreSQL to fully initialize

### Backend won't start
- Check if PostgreSQL is ready: `docker-compose logs postgres`
- Verify environment variables in `.env`
- Check backend logs: `docker-compose logs backend`

### Port already in use
- Change ports in `docker-compose.yml` if 8000 or 5432 are already in use
- Or stop the conflicting service

## Development

The backend service uses volume mounting for live code reloading. Changes to Python files will automatically reload the server.

For production, remove the `--reload` flag from the command in `docker-compose.yml`.

