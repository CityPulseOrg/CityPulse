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

| Method | Endpoint                      | Description                    |
|--------|-------------------------------|--------------------------------|
| GET    | `/`                           | API info                       |
| GET    | `/health`                     | Health check                   |
| POST   | `/reports`                    | Create a report                |
| GET    | `/reports`                    | List all reports               |
| GET    | `/reports/{id}`               | Get a single report            |
| PUT    | `/reports/{id}`               | Update a report                |
| DELETE | `/reports/{id}`               | Delete a report                |
| POST   | `/reports/{id}/followup`      | Submit follow-up clarification |

## Backboard AI Assistant Setup

CityPulse uses a Backboard AI assistant to analyze civic issue reports and enrich them with structured data (category, severity, priority, etc.).

### Creating the Assistant

1. **Set your Backboard API key** in `.env`:
   ```
   BACKBOARD_API_KEY=your_api_key_here
   ```

2. **Run the assistant creation script**:
   ```bash
   # If running in Docker
   docker compose exec backend python -m app.ai_workflow.assistant
   
   # If running locally
   python -m backend.app.ai_workflow.assistant
   ```

3. **The script will**:
   - Check if an assistant named "CPAssistant" already exists
   - If not, create a new assistant with the required schema
   - Print the Assistant ID and set it in the environment variable `ASSISTANT_ID`

4. **Save the Assistant ID**: Add it to your `.env` file:
   ```
   ASSISTANT_ID=your_assistant_id_here
   ```

### Assistant Schema

The assistant is configured with a `analyze_report` function that returns:

- **classification**: Category of the issue (pothole, broken_streetlight, etc.)
- **severity**: Level of severity (very_low to very_high)
- **priority**: Urgency level (not_urgent, urgent, very_urgent)
- **priority_score**: Numeric score 0-100 for prioritization
- **needs_clarification**: Boolean indicating if more info is needed
- **clarification**: Questions to ask the user (if needs_clarification is true)
- **number_of_matches**: Count of similar reports (provided by the backend)

### How Follow-up Works

When a report is created, the AI may determine that it `needs_clarification` and will set `clarification` with questions for the user.

1. **Initial Report**: User submits a report via `POST /reports`
   - Backend saves the images to disk and passes UploadFile objects to AI
   - AI analyzes and may request clarification
   - Report status may be set to "Waiting for user follow-up"

2. **Follow-up Flow**: User provides additional information via `POST /reports/{id}/followup`
   - Backend retrieves the existing report
   - Converts saved image filenames to full local paths
   - Queries database for similar reports (same category + nearby location)
   - Passes follow-up data + image paths + similar report count to AI
   - AI re-analyzes with new context
   - Backend updates the report with new AI response (category, severity, priority, etc.)
   - If clarification is no longer needed, status is updated

3. **Image Handling**:
   - **Initial report**: Images are UploadFile objects passed directly to AI
   - **Follow-up**: Images are loaded from disk paths and sent to AI
   - All images are stored in `uploads/` directory

4. **Similar Reports Query**:
   - Backend counts similar reports using:
     - Same category (if known)
     - Nearby location (±0.01 degrees, ~1km radius)
   - Count is passed to AI to help with analysis
   - AI uses this to populate `number_of_matches` field

## Environment Variables

| Variable              | Description                    |
|-----------------------|--------------------------------|
| POSTGRES_USER         | Database username              |
| POSTGRES_PASSWORD     | Database password              |
| POSTGRES_DB           | Database name                  |
| BACKBOARD_API_KEY     | Backboard API key              |
| ASSISTANT_ID          | Backboard assistant ID         |
| VITE_API_URL          | Backend URL for frontend       |
