# ============================================
# Root Dockerfile for Railway - Backend deployment
# Updated to use run.py for proper PORT handling
# ============================================

FROM python:3.11-slim

# Bust cache to force rebuild
ARG CACHEBUST=20251114145500

# Set working directory
WORKDIR /app

# Copy requirements from backend directory (build context is root)
COPY backend/requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend application files
COPY backend/ ./

# Expose port
EXPOSE 8000

# Start with Python script to properly handle PORT variable
# Using ENTRYPOINT to prevent Railway from overriding it
ENTRYPOINT ["python", "run.py"]
