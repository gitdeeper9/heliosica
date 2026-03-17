# HELIOSICA Dockerfile
# Heliospheric Event and L1 Integrated Observatory for Solar Intelligence and Coronal Activity
# Version: 1.0.0 | DOI: 10.5281/zenodo.19082026

FROM python:3.10-slim as builder

LABEL maintainer="Samir Baladi <gitdeeper@gmail.com>"
LABEL version="1.0.0"
LABEL description="HELIOSICA - Nine Parameters to Decode the Solar Wind and Shield Our Digital World"
LABEL doi="10.5281/zenodo.19082026"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libhdf5-dev \
    libnetcdf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install HELIOSICA
RUN pip install -e .

# ============================================
# Production stage
# ============================================
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libhdf5-dev \
    libnetcdf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Create non-root user
RUN useradd -m -u 1000 heliosica && chown -R heliosica:heliosica /app
USER heliosica

# Create directories
RUN mkdir -p /app/data /app/logs /app/output /app/config

# Environment variables
ENV HELIOSICA_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose ports
EXPOSE 5000 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run HELIOSICA
CMD ["heliosica", "serve", "--host", "0.0.0.0", "--port", "5000"]
