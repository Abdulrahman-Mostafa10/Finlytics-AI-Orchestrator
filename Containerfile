# Use official Python runtime
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uvicorn (correct package name)
RUN pip install --no-cache-dir uvicorn

# Set working directory
WORKDIR /app

COPY requirements-linux.txt .

RUN pip install --no-cache-dir -r requirements-linux.txt

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port 8001 (matches your app and pipeline)
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/ping || exit 1

# Command to run your application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
