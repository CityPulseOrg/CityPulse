# CityPulse

AI-powered civic issue reporting system.

## Quick Start (Docker)

The fastest way to get CityPulse running:

```bash
# 1. Clone the repository
git clone https://github.com/CityPulseOrg/CityPulse.git
cd CityPulse

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env and add your Backboard API key (required)

# 3. Start all services
docker compose up --build
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Setup

### Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **For local development:**
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 15+

### Environment Configuration

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and configure required variables:**

   **Required:**
   - `BACKBOARD_API_KEY`: Your Backboard AI API key ([get one here](https://backboard.ai))
   
   **Database (defaults work for Docker):**
   - `POSTGRES_USER`: Database username (default: `citypulse`)
   - `POSTGRES_PASSWORD`: Database password (change for production!)
   - `POSTGRES_DB`: Database name (default: `citypulse`)
   - `DATABASE_URL`: Connection string (for local dev: `postgresql://citypulse:PASSWORD@localhost:5432/citypulse`)
   
   **Optional:**
   - `ASSISTANT_ID`: Backboard AI assistant ID (auto-created if not set)
   - `BACKBOARD_API_URL`: API URL (default: `https://api.backboard.ai`)
   - `CORS_ORIGINS`: Comma-separated allowed origins (empty = dev defaults)
   - `DEBUG`: Enable debug mode (`true`/`false`)
   - `NEXT_PUBLIC_API_BASE_URL`: Backend URL for frontend (default: `http://localhost:8000`)

3. **Important notes:**
   - Never commit `.env` to version control (already in `.gitignore`)
   - For local development outside Docker, set `DATABASE_URL` to use `localhost:5432`
   - For production, change `POSTGRES_PASSWORD` and restrict `CORS_ORIGINS`

### Option 1: Docker Development (Recommended)

**Advantages:** No need to install Python, Node.js, or PostgreSQL locally. Everything runs in containers.

```bash
# Start all services (database, backend, frontend)
docker compose up --build

# Run in background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Reset database (removes all data)
docker compose down -v
```

### Option 2: Local Development

Run services locally for faster iteration and debugging.

#### Backend Setup

1. **Install Python 3.11+** (check with `python --version`)

2. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate (Linux/Mac)
   source .venv/bin/activate
   
   # Activate (Windows)
   .venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Ensure PostgreSQL is running locally** (or use Docker for just the database):
   ```bash
   # Option: Run only PostgreSQL in Docker
   docker compose up -d db
   ```

5. **Update `.env`** to use localhost:
   ```bash
   DATABASE_URL=postgresql://citypulse:citypulse@localhost:5432/citypulse
   ```

6. **Run database migrations:**
   ```bash
   cd backend
   alembic upgrade head
   cd ..
   ```

7. **Start the backend:**
   ```bash
   # From repository root (so .env is loaded)
   uvicorn backend.app.main:app --reload --port 8000
   ```

#### Frontend Setup

1. **Install Node.js 20+** (check with `node --version`)

2. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   
   Frontend will be available at http://localhost:3000

4. **Build for production:**
   ```bash
   npm run build
   npm start
   ```
   
   The build creates a standalone server at `.next/standalone/server.js` (used by Docker).

### Verifying Your Setup

1. **Check backend health:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy", "database": "connected"}
   ```

2. **Check API documentation:**
   Open http://localhost:8000/docs in your browser

3. **Check frontend:**
   Open http://localhost:3000 in your browser

### Environment Variables Reference

| Variable                    | Required | Default                      | Description                                |
|-----------------------------|----------|------------------------------|--------------------------------------------|
| `POSTGRES_USER`             | Yes      | `citypulse`                  | Database username                          |
| `POSTGRES_PASSWORD`         | Yes      | (must set)                   | Database password                          |
| `POSTGRES_DB`               | Yes      | `citypulse`                  | Database name                              |
| `DATABASE_URL`              | Yes      | (auto in Docker)             | Full PostgreSQL connection string          |
| `BACKBOARD_API_KEY`         | **Yes**  | (none)                       | Backboard AI API key                       |
| `ASSISTANT_ID`              | No       | (empty)                      | Backboard assistant ID (auto-created)      |
| `BACKBOARD_API_URL`         | No       | `https://api.backboard.ai`   | Backboard API base URL                     |
| `CORS_ORIGINS`              | No       | (empty = dev defaults)       | Comma-separated allowed origins            |
| `DEBUG`                     | No       | `false`                      | Enable debug mode                          |
| `NEXT_PUBLIC_API_BASE_URL`  | No       | `http://localhost:8000`      | Backend API URL (frontend build-time var)  |

### GitHub Secrets (CI/CD)

For GitHub Actions to work, add these repository secrets:
(`Settings` → `Secrets and variables` → `Actions` → `New repository secret`)

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `BACKBOARD_API_KEY`
- `NEXT_PUBLIC_API_BASE_URL` (e.g., `http://localhost:8000` for preview builds)

## Docker Commands Reference

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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

See [LICENSE.txt](LICENSE.txt) for details.
