# ============================================
# Dockerfile - Backend Only (Updated for Railway) - v4
# Force rebuild: 2025-11-14T14:30:00Z
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

# Start with Python script (bypasses all shell variable issues)
CMD ["python", "run.py"]

