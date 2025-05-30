#!/bin/bash

# Grace Project Shutdown Script
# This script stops the Grace application and its dependencies

# Set the working directory to the project root
cd "$(dirname "$0")/.."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker and Docker Compose are required to run Grace."
    echo "Please install Docker and Docker Compose before continuing."
    exit 1
fi

# Check if the application is running
if [ -z "$(docker ps -q -f name=grace-app)" ]; then
    echo "Grace application is not running."
    exit 0
fi

# Stop the application with Docker Compose
echo "Stopping Grace application..."
docker-compose -f ./deployment/docker-compose.yml down

# Check if the application stopped successfully
if [ $? -eq 0 ]; then
    echo "Grace application stopped successfully!"
else
    echo "Error: Failed to stop Grace application."
    echo "Please check the logs for more information."
    exit 1
fi

# Ask if user wants to remove volumes
read -p "Do you want to remove all data volumes? This will delete all user data and memories. (y/N): " remove_volumes

if [[ "$remove_volumes" =~ ^[Yy]$ ]]; then
    echo "Removing data volumes..."
    docker-compose -f ./deployment/docker-compose.yml down -v
    echo "Data volumes removed."
fi

exit 0
