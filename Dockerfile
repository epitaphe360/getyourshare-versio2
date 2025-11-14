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

# Bust cache RIGHT BEFORE copying application files to force fresh copy
ARG CACHEBUST=20251114151500

# Copy all backend application files (cache busted - will always copy fresh)
COPY backend/ ./

# Expose port
EXPOSE 8000

# Start with Python script to properly handle PORT variable
# Using ENTRYPOINT to prevent Railway from overriding it
ENTRYPOINT ["python", "run.py"]
