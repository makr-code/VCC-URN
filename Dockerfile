# Multi-stage Dockerfile for VCC-URN Resolver
# Production-ready with security best practices

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-alpine

# Install runtime dependencies (curl for healthcheck, libpq for psycopg)
RUN apk add --no-cache \
    curl \
    libpq

# Create non-root user
RUN adduser --disabled-password --gecos "" --uid 65534 nonroot

# Copy Python packages from builder
COPY --from=builder /root/.local /home/nonroot/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=nonroot:nonroot . .

# Set environment variables
ENV PATH=/home/nonroot/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER nonroot

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/healthz || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
