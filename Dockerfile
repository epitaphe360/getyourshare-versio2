# ============================================
# Root Dockerfile for Railway - Backend deployment
# Updated to use run.py for proper PORT handling
# ============================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements from backend directory (build context is root)
COPY backend/requirements.txt ./

# Install dependencies - Changed to force rebuild
RUN pip install -r requirements.txt

# ABSOLUTE CACHE KILLER - Multiple random operations
RUN date > /tmp/build_timestamp.txt && cat /tmp/build_timestamp.txt
RUN echo "Build ID: railway-$(date +%s)" && ls -la

# Copy all backend application files - NO CACHE POSSIBLE
COPY backend/ ./

# Verify correct file was copied
RUN head -10 db_queries_real.py | grep "from utils.logger import logger" || (echo "ERROR: Wrong file version!" && exit 1)

# Expose port
EXPOSE 8000

# Start with Python script to properly handle PORT variable
# Using ENTRYPOINT to prevent Railway from overriding it
ENTRYPOINT ["python", "run.py"]
