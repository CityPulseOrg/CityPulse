# CityPulse Setup Guide

This guide walks you through setting up CityPulse from a fresh clone.

## Prerequisites Check

Before starting, ensure you have:

- [ ] Docker and Docker Compose installed
  ```bash
  docker --version
  docker compose version
  ```

- [ ] Backboard AI API key ([get one here](https://backboard.ai))

**OR** for local development:

- [ ] Python 3.11+ (`python --version`)
- [ ] Node.js 20+ (`node --version`)
- [ ] PostgreSQL 15+ (`psql --version`)

## Step-by-Step Setup

### 1. Clone Repository

```bash
git clone https://github.com/CityPulseOrg/CityPulse.git
cd CityPulse
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your editor
nano .env  # or vim, code, etc.
```

**Required changes in `.env`:**
- Set `BACKBOARD_API_KEY=your_actual_api_key_here`
- Change `POSTGRES_PASSWORD` to a secure password (production only)

### 3. Start Services (Docker)

```bash
# Build and start all services
docker compose up --build

# Or run in background
docker compose up -d --build
```

**Wait for services to start** (usually 30-60 seconds for first build).

### 4. Verify Installation

Open your browser and check:

1. **Frontend**: http://localhost:3000
   - Should show CityPulse homepage
   
2. **Backend API**: http://localhost:8000
   - Should return JSON with API info
   
3. **API Documentation**: http://localhost:8000/docs
   - Should show interactive Swagger UI
   
4. **Health Check**: http://localhost:8000/health
   - Should return: `{"status": "healthy", "database": "connected"}`

### 5. Test the Application

1. Go to http://localhost:3000
2. Click "Report an Issue"
3. Fill in the form and submit
4. Check if the report appears in the list

## Troubleshooting

### Services won't start

**Check Docker logs:**
```bash
docker compose logs backend
docker compose logs db
```

**Common issues:**
- Port already in use (3000 or 8000)
  - Stop other services using these ports
  - Or change ports in `docker-compose.yml`
  
- Database connection failed
  - Ensure database service is healthy: `docker compose ps`
  - Check environment variables in `.env`

### Backend can't connect to database

1. Verify `.env` has correct database credentials
2. Check database is running: `docker compose ps`
3. Test database connection:
   ```bash
   docker compose exec db psql -U citypulse -d citypulse -c "SELECT 1;"
   ```

### Frontend can't reach backend

1. Check `NEXT_PUBLIC_API_BASE_URL` in `.env` (should be `http://localhost:8000`)
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check CORS logs in backend: `docker compose logs backend | grep CORS`

### BACKBOARD_API_KEY errors

1. Ensure you have a valid API key from https://backboard.ai
2. Check the key is set in `.env` (no quotes, no spaces)
3. Restart services after changing `.env`: `docker compose restart`

## Local Development Setup (Without Docker)

If you prefer to run services locally:

### Backend

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Set up local database
# Ensure PostgreSQL is running, then:
cd backend
alembic upgrade head
cd ..

# 4. Start backend (from repo root)
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Start development server
npm run dev
```

## Next Steps

- Read the [main README](README.md) for API documentation
- Check [backend/MIGRATIONS.md](backend/MIGRATIONS.md) for database migration info
- Set up the Backboard AI assistant (see README)
- Deploy to production (see deployment guides)

## Getting Help

- Check [GitHub Issues](https://github.com/CityPulseOrg/CityPulse/issues)
- Review [GitHub Discussions](https://github.com/CityPulseOrg/CityPulse/discussions)
- Read the [API Documentation](http://localhost:8000/docs) (when running)
