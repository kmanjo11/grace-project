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

