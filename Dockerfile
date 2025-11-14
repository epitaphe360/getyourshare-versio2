# ============================================
# Root Dockerfile for Railway - Monorepo setup - Fixed
# ============================================

FROM python:3.11-slim

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

# Start the application
CMD ["sh", "-c", "uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}"]
