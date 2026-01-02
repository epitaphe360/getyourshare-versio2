# ============================================
# Root Dockerfile for Railway - Monorepo setup - Production Ready
# ============================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for Python to avoid buffering issues
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Copy requirements from backend directory (build context is root)
COPY backend/requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy run script first (it handles PORT from env)
COPY backend/run.py ./

# Copy all backend application files
COPY backend/ ./

# Expose port 
EXPOSE 8000

# Health check endpoint verification
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT:-8000}/health', timeout=5)"

# Use Python script for startup - handles PORT environment variable properly
CMD ["python", "run.py"]

