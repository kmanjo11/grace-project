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
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install pip-tools and pipreqs first
RUN pip install --no-cache-dir pip-tools pipreqs

# Install Python deps with specific versions
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create installation script with enhanced dependency detection
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Starting dependency installation ===\\n"\n\
\n\
# Try exact versions first\nif [ -f "requirements.txt" ]; then\n    echo "1. Attempting to install exact versions from requirements.txt..."\n    if pip install --no-cache-dir -r requirements.txt; then\n        echo "✓ Successfully installed all dependencies from requirements.txt!\\n"\n        exit 0\n    fi\n    echo "⚠ Could not install exact versions, falling back...\\n"\nfi\n\n# Try to detect dependencies from code\necho "2. Analyzing codebase for required packages..."\nif command -v pipreqs &> /dev/null; then\n    echo "3. Generating requirements from code analysis..."\n    if pipreqs --mode no-pin --savepath=requirements_detected.txt .; then\n        if [ -f "requirements_detected.txt" ]; then\n            echo "4. Installing detected requirements..."\n            if pip install --no-cache-dir -r requirements_detected.txt; then\n                echo "✓ Successfully installed detected dependencies!\\n"\n                exit 0\n            fi\n        fi\n    fi\nfi\n\n# Fallback to requirements.in if exists\nif [ -f "requirements.in" ]; then\n    echo "5. Falling back to requirements.in with pip-compile..."\n    echo "6. Generating new requirements from requirements.in..."\n    if pip-compile --generate-hashes --output-file=requirements.tmp requirements.in; then\n        echo "7. Installing compiled requirements..."\n        if pip install --no-cache-dir -r requirements.tmp; then\n            echo "✓ Successfully installed dependencies from requirements.in!\\n"\n            exit 0\n        fi\n    fi\nfi\n\n# Last resort: minimal working set\necho "⚠ Falling back to minimal working set...\\n"\necho "8. Installing minimal working set of dependencies..."\npip install --no-cache-dir fastapi uvicorn python-multipart python-jose[cryptography] \\\n    python-dotenv requests solana numpy pandas scikit-learn\n\necho "✓ Installed minimal working set of dependencies\\n"
' > /usr/local/bin/install-deps && \
    chmod +x /usr/local/bin/install-deps

# ============================
# PRODUCTION STAGE
# ============================
FROM python:3.11-slim

# Create app user and set up directories
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p /app/data/chromadb /app/logs && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy application code from builder
COPY --from=builder /app /app

# Install dependencies as root
RUN if [ -f "requirements.txt" ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    fi && \
    chmod 755 /app /app/data /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user for runtime
USER appuser:appuser

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV GRACE_ENV=production
ENV LOG_LEVEL=info
ENV OPENAI_API_KEY=${OPENAI_API_KEY:-your-default-key-here}

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "src/run_server.py"]