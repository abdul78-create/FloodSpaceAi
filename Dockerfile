# FloodSpaceAI — Reproducible Evaluation Container
# Track B: Mapping Flood Damage from Space (Multimodal AI Hackathon 2026)

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies, GDAL, Python 3.10, and Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python3-gdal \
    gdal-bin \
    libgdal-dev \
    curl \
    git \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Dashboard Node dependencies
COPY dashboard/package*.json /app/dashboard/
RUN cd /app/dashboard && npm install

# Copy application source
COPY . /app/

# Build Next.js production dashboard
RUN cd /app/dashboard && npm run build

# Expose Next.js port
EXPOSE 3000

# Default command: launch dashboard server
CMD ["sh", "-c", "cd /app/dashboard && npm run dev"]
