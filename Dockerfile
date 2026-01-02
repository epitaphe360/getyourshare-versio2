# ============================================
# Root Dockerfile for Railway - Backend deployment
# Updated to use run.py for proper PORT handling
# Build ID: 2026-01-02-v2 (force cache invalidation)
# ============================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for Python to avoid buffering issues
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Force cache bust for requirements
ARG CACHEBUST=1

# Copy requirements from backend directory (build context is root)
COPY backend/requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Force rebuild of application files - timestamp: 2026-01-02T18:15:00
COPY backend/ ./

# Expose port 
EXPOSE 8000

# Use Python script for startup - handles PORT environment variable properly
CMD ["python", "run.py"]
