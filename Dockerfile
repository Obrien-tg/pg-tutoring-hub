# Multi-stage Dockerfile for production
FROM python:3.12-slim AS builder

# Set work directory
WORKDIR /app

# Install system deps for building
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cache layer)
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install runtime system deps
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy app
COPY . .

# Make sure scripts are executable
RUN chmod +x manage.py

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose port
EXPOSE 8000

# Set environment
ENV PATH=/root/.local/bin:$PATH

# Run with Gunicorn
CMD ["gunicorn", "pg_hub.wsgi:application", "--bind", "0.0.0.0:8000"]