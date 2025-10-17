# Multi-stage build for Hedge Mode Trading Bot
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt para_requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage for development/runtime
FROM base as runtime

# Create logs directory
RUN mkdir -p /app/logs

# Copy application code
COPY . .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash hedge && \
    chown -R hedge:hedge /app

USER hedge

# Set default command
CMD ["python", "hedge_mode.py", "--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"