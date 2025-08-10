#!/bin/bash

# Grace Project Docker Deployment Script
# This script builds and runs the Grace project in Docker

set -e

# Navigate to the project directory
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)

echo "===== Deploying Grace Docker Environment ====="
echo "Project directory: $PROJECT_DIR"

# Check if .env file exists, create if not
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Creating .env file with default values..."
    cat > "$PROJECT_DIR/.env" << EOL
# Grace Environment Configuration
GRACE_ENV=production
DEBUG=false
LOG_LEVEL=info

# Security Settings
JWT_SECRET=$(openssl rand -hex 32)
FERNET_KEY=$(openssl rand -base64 32)
SESSION_EXPIRY=86400

# Database Settings
CHROMA_DB_PATH=/app/data/chromadb
PROFILE_DATA_PATH=/app/data/profiles.json

# Solana Settings
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=aa07df83-e1ac-4117-b00d-173e94e4fff7
SOLANA_NETWORK=mainnet-beta

# OpenAI Settings (replace with your API key)
OPENAI_API_KEY=your_openai_api_key_here
EOL
    echo "Please edit .env file to set your OpenAI API key"
fi

# Build and start the containers
echo "Building and starting Docker containers..."
docker-compose -f deployment/docker-compose.yml up -d --build

# Wait for the application to start
echo "Waiting for the application to start..."
sleep 10

# Check if the containers are running
echo "Checking container status..."
CONTAINERS=$(docker-compose -f deployment/docker-compose.yml ps -q)
for CONTAINER in $CONTAINERS; do
    STATUS=$(docker inspect --format='{{.State.Status}}' $CONTAINER)
    NAME=$(docker inspect --format='{{.Name}}' $CONTAINER | sed 's/\///')
    echo "$NAME: $STATUS"
    if [ "$STATUS" != "running" ]; then
        echo "Error: Container $NAME is not running."
        echo "Checking logs for $NAME..."
        docker logs $CONTAINER
        exit 1
    fi
done

echo "===== Grace Docker Environment is now running ====="
echo "Access the UI at: http://localhost:9000"
echo "To stop the environment, run: ./deployment/stop_docker.sh"
