# CityPulse Backend Dockerfile
# FastAPI application with Python 3.11

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \     
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* 
#gcc: compiler
#libpq: PostgreSQL dev libs
#curl: for health check 


# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#Run uvicorn server, load fastapi main app, host on 0.0.0.0 (klisten inside and outside of container), keep running forever and listen on port 8000
#Will eventually need to override CMD for prod