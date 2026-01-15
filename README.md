# CityPulse

AI-powered civic issue reporting system.

## Quick Start

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env and add your Backboard API credentials

# 3. Run everything
docker compose up --build
```

## Environment Setup

- Copy the example file and edit your values: `cp .env.example .env`
- Variables used locally and in CI:
   - POSTGRES_USER: database username (e.g., `citypulse`)
   - POSTGRES_PASSWORD: database password (e.g., `citypulse`)
   - POSTGRES_DB: database name (e.g., `citypulse`)
   - DATABASE_URL: local-only connection (outside Docker): `postgresql://citypulse:citypulse@localhost:5432/citypulse`
   - BACKBOARD_API_KEY: Backboard API key (secret)
   - BACKBOARD_WORKFLOW_ID: optional Backboard workflow ID (if applicable)
   - BACKBOARD_API_URL: Backboard API base URL (default `https://api.backboard.ai`)
   - VITE_API_URL: frontend’s API base URL (e.g., `http://localhost:8000`)

### GitHub Secrets (Actions → Secrets and variables → Actions)

Add these repository secrets so CI can verify and inject them:
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB
- BACKBOARD_API_KEY
- VITE_API_URL

Recommendation:
- Use the same values as your local `.env` for POSTGRES_* to keep consistency.
- Set `VITE_API_URL` to `http://localhost:8000` for preview builds, or your deployed URL per environment.

## Docker Commands

```bash
# Start all services (with build)
docker compose up --build

# Start in background (detached mode)
docker compose up -d --build

# Stop all services
docker compose down

# Stop and remove volumes (wipes database)
docker compose down -v

# View logs
docker compose logs

# View logs for specific service
docker compose logs backend
docker compose logs db

# Follow logs in real-time
docker compose logs -f

# Restart a specific service
docker compose restart backend

# Rebuild a specific service
docker compose up --build backend

# Check running containers
docker compose ps
```

## Run Outside Docker (Local Dev)

If you prefer to run the backend without Docker:

```bash
# 1) Ensure Postgres is running locally and .env is set
cp .env.example .env
# Verify DATABASE_URL points to localhost:5432

# 2) Create a virtual environment and install deps
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 3) Start the API from the repo root so .env is loaded
uvicorn backend.app.main:app --reload --port 8000
```

Notes:
- Running from the repo root ensures `.env` is picked up by the app settings.
- Use `http://localhost:8000/health` to confirm DB connectivity.

## Services

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000        |
| Backend  | http://localhost:8000        |
| API Docs | http://localhost:8000/docs   |
| Health   | http://localhost:8000/health |

## Database Connection

- Local tools: postgresql://citypulse:citypulse@localhost:5432/citypulse
- Inside Docker: postgresql://citypulse:citypulse@db:5432/citypulse
- Hostnames: use `localhost` from your machine; use `db` from containers
- Port: 5432 is published to the host by docker-compose

## Database Migrations

Database schema is managed with Alembic migrations. Migrations run automatically on container startup.

**Key features:**
- ✅ Automatic schema creation on first run
- ✅ Startup DB connection test (fails fast if DB is broken)
- ✅ Migration history tracking

For detailed migration commands and troubleshooting, see [backend/MIGRATIONS.md](backend/MIGRATIONS.md).

### Quick commands

```bash
# Check current migration version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# Create a new migration after modifying models
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## Architecture

```
Citizens -> Frontend -> Backend API -> Backboard AI Workflow
                            |
                         PostgreSQL
```

- **Frontend**: Web UI for submitting reports
- **Backend**: FastAPI REST API
- **Database**: PostgreSQL for storing reports
- **AI**: Backboard workflow handles classification, severity, and email drafting

## API Endpoints

| Method | Endpoint           | Description         |
|--------|--------------------|---------------------|
| GET    | `/`                | API info            |
| GET    | `/health`          | Health check        |
| POST   | `/reports`         | Create a report     |
| GET    | `/reports`         | List all reports    |
| GET    | `/reports/{id}`    | Get a single report |
| PUT    | `/reports/{id}`    | Update a report     |
| DELETE | `/reports/{id}`    | Delete a report     |

## Environment Variables

| Variable              | Description                    |
|-----------------------|--------------------------------|
| POSTGRES_USER         | Database username              |
| POSTGRES_PASSWORD     | Database password              |
| POSTGRES_DB           | Database name                  |
| BACKBOARD_API_KEY     | Backboard API key              |
| VITE_API_URL          | Backend URL for frontend       |
