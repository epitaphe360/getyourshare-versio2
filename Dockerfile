# ============================================
# Root Dockerfile for Railway - Backend deployment
# Updated to use run.py for proper PORT handling
# Build ID: 2026-01-05-v4 (FORCE ALL CACHE BUST)
# ============================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for Python to avoid buffering issues
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Force cache bust - change this value to force rebuild
ARG BUILD_TIMESTAMP=20260105v4

# Copy requirements from backend directory (build context is root)
COPY backend/requirements.txt ./

# Install dependencies - Changed to force rebuild
RUN pip install -r requirements.txt

# ABSOLUTE CACHE KILLER - Multiple random operations
RUN date > /tmp/build_timestamp.txt && cat /tmp/build_timestamp.txt
RUN echo "Build ID: railway-$(date +%s)" && ls -la

# Copy all backend application files - NO CACHE POSSIBLE
COPY backend/ ./

# Expose port 
EXPOSE 8000

# Start with Python script to properly handle PORT variable
# Using ENTRYPOINT to prevent Railway from overriding it
ENTRYPOINT ["python", "run.py"]
