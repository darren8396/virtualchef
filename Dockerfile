# VirtualChef - Dockerfile for Google Cloud Run
# Optimized for Streamlit applications

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cloud Run expects port 8080
ENV PORT=8080

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for certain packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/_stcore/health || exit 1

# Run Streamlit
# --server.address=0.0.0.0 binds to all interfaces (required for containers)
# --server.port uses the PORT env var (Cloud Run injects this)
# --server.enableCORS=false and --server.enableXsrfProtection=false for Cloud Run compatibility
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false
