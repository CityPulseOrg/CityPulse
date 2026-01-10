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

## Services

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000        |
| Backend  | http://localhost:8000        |
| API Docs | http://localhost:8000/docs   |
| Health   | http://localhost:8000/health |

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
