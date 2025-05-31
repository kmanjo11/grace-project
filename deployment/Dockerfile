# ============================
# BUILDER STAGE
# ============================
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python deps with specific versions
RUN pip install --user -r requirements.txt


# Install pip-tools and pipreqs early
RUN pip install --user pip-tools pipreqs

# Copy application code first for dependency analysis
COPY . .

# Create installation script with enhanced dependency detection
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Starting dependency installation ===\\n"\n\
\n\
# Try exact versions first\n\
if [ -f "requirements.txt" ]; then\n\
    echo "1. Attempting to install exact versions from requirements.txt..."\n\
    if pip install --user -r requirements.txt; then\n\
        echo "✓ Successfully installed all dependencies from requirements.txt!\\n"\n\
        exit 0\n\
    fi\n\
    echo "⚠ Could not install exact versions, falling back...\\n"\n\
fi\n\
\n\
# Try to detect dependencies from code\n\
echo "2. Analyzing codebase for required packages..."\n\
if command -v pipreqs &> /dev/null; then\n\
    echo "3. Generating requirements from code analysis..."\n\
    if pipreqs --mode no-pin --savepath=requirements_detected.txt .; then\n\
        if [ -f "requirements_detected.txt" ]; then\n\
            echo "4. Installing detected requirements..."\n\
            if pip install --user -r requirements_detected.txt; then\n\
                echo "✓ Successfully installed detected dependencies!\\n"\n\
                exit 0\n\
            fi\n\
        fi\n\
    fi\n\
fi\n\
\n\
# Fallback to requirements.in if exists\n\
if [ -f "requirements.in" ]; then\n\
    echo "5. Falling back to requirements.in with pip-compile..."\n\
    pip install --user pip-tools\n\
    echo "6. Generating new requirements from requirements.in..."\n\
    pip-compile --generate-hashes --output-file=requirements.tmp requirements.in\n\
    \n    echo "7. Installing compiled requirements..."\n    if pip install --user -r requirements.tmp; then\n        echo "✓ Successfully installed dependencies from requirements.in!\\n"\n        exit 0\n    fi\nfi\n\
\n\
# Last resort: minimal working set\necho "⚠ Falling back to minimal working set...\\n"\necho "8. Installing minimal working set of dependencies..."\npip install --user fastapi uvicorn python-multipart python-jose[cryptography] \\\n    python-dotenv requests solana \\\n    numpy pandas scikit-learn\n\necho "✓ Installed minimal working set of dependencies\\n"\n\
' > /usr/local/bin/install-deps && \
    chmod +x /usr/local/bin/install-deps

# ============================
# PRODUCTION STAGE
# ============================
FROM python:3.10-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/local/bin/install-deps /usr/local/bin/

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Install dependencies using our script
RUN install-deps

# Create necessary directories
RUN mkdir -p data/chromadb logs

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