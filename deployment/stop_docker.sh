#!/bin/bash

# Grace Project Docker Stop Script
# This script stops the Grace Docker environment

set -e

# Navigate to the project directory
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)

echo "===== Stopping Grace Docker Environment ====="

# Stop the containers
echo "Stopping Docker containers..."
docker-compose -f deployment/docker-compose.yml down

echo "===== Grace Docker Environment has been stopped ====="
