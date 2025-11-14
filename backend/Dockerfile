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

# Make all start scripts executable
RUN chmod +x start.sh start-fast.sh

# Expose port
EXPOSE 8000

# Start with minimal server by default (faster, always works)
# To use full server, change Railway start command to: ./start.sh
CMD ["./start-fast.sh"]

