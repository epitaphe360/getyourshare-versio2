# ============================================
# Dockerfile - Backend Only (Updated for Railway) - v3
# ============================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Start the application with proper PORT handling
# Using sh -c to ensure shell variable substitution works
CMD sh -c 'exec uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}'

