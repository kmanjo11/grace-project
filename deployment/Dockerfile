# ============================
# BUILDER STAGE
# ============================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .


# Install Python deps with specific versions
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# ============================
# PRODUCTION STAGE
# ============================
FROM python:3.11-slim

# Set working directory to /app
WORKDIR /app
# Install runtime dependencies for open-interpreter
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    python3-pip \
    python3-venv \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages and source code
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/requirements.txt .
COPY --from=builder /app/src /app/src
COPY --from=builder /app/user_profile_system.py /app/src/

# Copy Next.js build files for frontend
COPY src/ui/out /app/static

# Reinstall open-interpreter in the final image to ensure all dependencies are properly linked
RUN pip install --no-cache-dir open-interpreter>=0.1.13

# In the production stage, add this right after the Python packages are copied:
RUN pip install --no-cache-dir solana

# Add build argument for OpenAI API key
ARG OPENAI_API_KEY

# Environment variables
ENV PYTHONPATH=/app/src:${PYTHONPATH} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    GRACE_ENV=production \
    LOG_LEVEL=info \
    OPENAI_API_KEY=${OPENAI_API_KEY}


# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "src/run_server.py"]