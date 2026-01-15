# Database Migrations

This document describes how to manage database schema changes using Alembic.

## Overview

The backend uses Alembic for database migrations. Migrations are automatically applied on container startup via the `entrypoint.sh` script.

## Directory Structure

```
backend/
├── alembic/
│   ├── versions/          # Migration files
│   │   └── 001_initial_schema.py
│   ├── env.py            # Alembic environment config
│   └── script.py.mako    # Template for new migrations
├── alembic.ini           # Alembic configuration
└── entrypoint.sh         # Runs migrations before app starts
```

## Automatic Migrations (Docker)

When you start the backend with Docker Compose, migrations run automatically:

```bash
docker-compose up backend
```

The `entrypoint.sh` script runs `alembic upgrade head` before starting the FastAPI server.

## Manual Migration Commands

If you need to run migrations manually (development/debugging):

### Apply all pending migrations
```bash
# In Docker container:
docker-compose exec backend alembic upgrade head

# Or locally (if you have the environment set up):
cd backend
alembic upgrade head
```

### Check current migration version
```bash
alembic current
```

### Show migration history
```bash
alembic history
```

### Downgrade to previous version
```bash
alembic downgrade -1
```

## Creating New Migrations

When you modify the database models in `app/models.py`:

### Auto-generate migration from model changes
```bash
# In the backend directory:
alembic revision --autogenerate -m "Description of changes"
```

This will:
1. Compare your models against the current database schema
2. Generate a new migration file in `alembic/versions/`
3. Include detected changes (new tables, columns, indexes, etc.)

### Manually create an empty migration
```bash
alembic revision -m "Description of changes"
```

Then edit the generated file to add your custom upgrade/downgrade logic.

## Current Schema

The initial migration (`001_initial_schema.py`) creates:

- **issues** table: Stores citizen reports with AI-enriched metadata
  - Core fields: id, title, description, status, location
  - AI fields: thread_id, category, severity, priority, etc.
  
- **issue_events** table: Audit log of events related to issues
  - Links to issues via foreign key

## Troubleshooting

### Database connection fails on startup
The application has a startup check that validates database connectivity. If this fails:
- Check DATABASE_URL environment variable
- Ensure PostgreSQL container is running
- Verify network connectivity between containers

### Migration fails
If a migration fails:
```bash
# Check current version
alembic current

# View migration history
alembic history --verbose

# Manually fix the issue, then try again
alembic upgrade head
```

### Reset database (destructive!)
```bash
# Drop all tables and re-run migrations
docker-compose down -v  # Removes volumes
docker-compose up backend
```

## Best Practices

1. **Always review auto-generated migrations** before applying them
2. **Test migrations** on a copy of production data before deploying
3. **Make migrations reversible** when possible (implement downgrade())
4. **One logical change per migration** for easier rollback
5. **Never edit applied migrations** - create a new migration instead
