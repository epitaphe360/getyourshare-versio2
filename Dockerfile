# ============================================
# Root Dockerfile for Railway - Backend deployment
# Updated to use run.py for proper PORT handling
# ============================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements from backend directory (build context is root)
COPY backend/requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# FORCE CACHE INVALIDATION - RUN command ensures Docker rebuilds everything after this
ARG CACHEBUST=20251114152000
RUN echo "Cache bust: ${CACHEBUST}"

# Copy all backend application files (will NOT use cache due to RUN above)
COPY backend/ ./

# Expose port
EXPOSE 8000

# Start with Python script to properly handle PORT variable
# Using ENTRYPOINT to prevent Railway from overriding it
ENTRYPOINT ["python", "run.py"]
