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

# Create an unprivileged user before copying application files so the
# runtime filesystem is owned by the account that serves the application.
RUN groupadd -r app && useradd -r -g app -d /home/app -s /sbin/nologin -m app \
    && mkdir -p /home/app/.local /app

# Copy app
COPY . .

# Copy installed packages into the runtime user's local bin.
COPY --from=builder /root/.local /home/app/.local

RUN mkdir -p /app/backend/media \
    && chown -R app:app /app /home/app

# Switch to the Django project package so manage.py and gunicorn
# resolve the backend modules without extra PYTHONPATH setup.
WORKDIR /app/backend

# Run build-time Django commands with the same user as the runtime process.
USER app

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose port
EXPOSE 8000

# Set environment
ENV PATH=/home/app/.local/bin:$PATH

# Run with Gunicorn
CMD ["gunicorn", "pg_hub.wsgi:application", "--bind", "0.0.0.0:8000"]