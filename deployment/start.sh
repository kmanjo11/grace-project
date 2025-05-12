#!/bin/bash

# Grace Project Startup Script
# This script starts the Grace application and its dependencies

# Set the working directory to the project root
cd "$(dirname "$0")/.."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker and Docker Compose are required to run Grace."
    echo "Please install Docker and Docker Compose before continuing."
    exit 1
fi

# Check if .env.production exists
if [ ! -f "./deployment/.env.production" ]; then
    echo "Error: .env.production file not found."
    echo "Please create the .env.production file in the deployment directory."
    exit 1
fi

# Generate secure keys if placeholders are still in the .env file
if grep -q "replace_with_secure_random_string" "./deployment/.env.production"; then
    echo "Generating secure JWT secret..."
    JWT_SECRET=$(openssl rand -hex 32)
    sed -i "s/replace_with_secure_random_string/$JWT_SECRET/g" "./deployment/.env.production"
fi

if grep -q "replace_with_secure_fernet_key" "./deployment/.env.production"; then
    echo "Generating secure Fernet key..."
    # Generate a base64-encoded 32-byte key for Fernet
    FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    sed -i "s/replace_with_secure_fernet_key/$FERNET_KEY/g" "./deployment/.env.production"
fi

if grep -q "replace_with_random_string" "./deployment/nitter.conf"; then
    echo "Generating secure HMAC key for Nitter..."
    HMAC_KEY=$(openssl rand -hex 16)
    sed -i "s/replace_with_random_string/$HMAC_KEY/g" "./deployment/nitter.conf"
fi

# Create necessary directories
echo "Creating data directories..."
mkdir -p ./data/chromadb
mkdir -p ./logs

# Set proper permissions
echo "Setting permissions..."
chmod -R 755 ./data
chmod -R 755 ./logs

# Start the application with Docker Compose
echo "Starting Grace application..."
docker-compose -f ./deployment/docker-compose.yml up -d

# Check if the application started successfully
if [ $? -eq 0 ]; then
    echo "Grace application started successfully!"
    echo "Web interface available at: http://localhost:8000"
    echo "Logs can be viewed with: docker-compose -f ./deployment/docker-compose.yml logs -f"
else
    echo "Error: Failed to start Grace application."
    echo "Please check the logs for more information."
    exit 1
fi

exit 0
