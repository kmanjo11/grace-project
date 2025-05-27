### FRONTEND STAGE
FROM node:18 AS frontend-builder

WORKDIR /ui

# Copy package files first for better caching
COPY src/ui/package.json src/ui/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY src/ui/ ./

# Set environment variables for the build
ENV REACT_APP_API_URL=/api

# Build with TypeScript
RUN npm run build || (echo "BUILD FAILED - check console output above")

### BACKEND STAGE
FROM python:3.10-slim

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir litellm==1.10.3 && \
    pip install --no-cache-dir open-interpreter==0.4.3

# Copy entire backend project
COPY . .

# Copy built frontend from builder stage
COPY --from=frontend-builder /ui/dist ./src/ui/dist

# Make sure required dirs exist
RUN mkdir -p data/chromadb logs

# Env vars
ENV PYTHONPATH=/app
ENV PORT=8000
ENV GRACE_ENV=production
ENV LOG_LEVEL=info
ENV OPENAI_API_KEY=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

EXPOSE 8000

CMD ["python", "src/run_server.py"]

