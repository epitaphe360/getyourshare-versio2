# ============================================
# Dockerfile - Backend Only (Updated for Railway) - v5
# Force rebuild: 2025-11-14T14:45:00Z - Clear cache for db_helpers.py fix
# ============================================
FROM python:3.11-slim

# Bust cache to force rebuild with fixed db_helpers.py
ARG CACHEBUST=20251114144500

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

# Start with Python script (bypasses all shell variable issues)
# Using ENTRYPOINT instead of CMD to prevent Railway from overriding it
ENTRYPOINT ["python", "run.py"]

