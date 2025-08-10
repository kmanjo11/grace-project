#!/bin/bash

# Grace Project Docker Test Script
# This script tests the Docker deployment of the Grace project

set -e

echo "===== Testing Grace Docker Deployment ====="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "Docker and Docker Compose are installed."

# Navigate to the project directory
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)

echo "Project directory: $PROJECT_DIR"

# Build the Docker images
echo "Building Docker images..."
docker-compose -f deployment/docker-compose.yml build

# Start the containers
echo "Starting containers..."
docker-compose -f deployment/docker-compose.yml up -d

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
        docker-compose -f deployment/docker-compose.yml down
        exit 1
    fi
done

# Test the API
echo "Testing API connection..."
API_URL="http://localhost:9000/api/auth/verify"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ "$HTTP_CODE" = "401" ]; then
    echo "API connection successful (received expected 401 Unauthorized)"
else
    echo "Error: API connection failed. Expected 401, got $HTTP_CODE"
    docker-compose -f deployment/docker-compose.yml down
    exit 1
fi

# Test the UI
echo "Testing UI connection..."
UI_URL="http://localhost:9000/"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $UI_URL)

if [ "$HTTP_CODE" = "200" ]; then
    echo "UI connection successful"
else
    echo "Error: UI connection failed. Expected 200, got $HTTP_CODE"
    docker-compose -f deployment/docker-compose.yml down
    exit 1
fi

# Check for the enterprise module error in logs
echo "Checking for enterprise module error in logs..."
if docker logs grace-app 2>&1 | grep -q "ModuleNotFoundError: No module named 'enterprise'"; then
    echo "Error: Enterprise module error detected in logs."
    docker-compose -f deployment/docker-compose.yml down
    exit 1
else
    echo "No enterprise module error detected."
fi

# Stop the containers
echo "Stopping containers..."
docker-compose -f deployment/docker-compose.yml down

echo "===== Docker deployment test completed successfully ====="
exit 0
