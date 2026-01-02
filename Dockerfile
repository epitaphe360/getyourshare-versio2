# ============================================
# Root Dockerfile for Railway - Backend deployment
# Updated to use run.py for proper PORT handling
# Build ID: 2026-01-02-v3 (FORCE ALL CACHE BUST)
# ============================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for Python to avoid buffering issues
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Force cache bust - change this value to force rebuild
ARG BUILD_TIMESTAMP=20260102v3

# Copy requirements from backend directory (build context is root)
COPY backend/requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Force rebuild by making ARG visible to this layer
RUN echo "Build timestamp: ${BUILD_TIMESTAMP}"

# Copy all backend files - this should now NOT use cache
COPY backend/ ./

# Expose port 
EXPOSE 8000

# Use Python script for startup - handles PORT environment variable properly
CMD ["python", "run.py"]
