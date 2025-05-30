#!/bin/bash

# Grace Project Backup Script
# This script creates a backup of the Grace application data

# Set the working directory to the project root
cd "$(dirname "$0")/.."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required to backup Grace data."
    echo "Please install Docker before continuing."
    exit 1
fi

# Create backup directory if it doesn't exist
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/grace_backup_$TIMESTAMP.tar.gz"

# Check if the application is running
if [ -z "$(docker ps -q -f name=grace-app)" ]; then
    echo "Warning: Grace application is not running. Backup may be incomplete."
    read -p "Continue anyway? (y/N): " continue_backup
    if [[ ! "$continue_backup" =~ ^[Yy]$ ]]; then
        echo "Backup aborted."
        exit 0
    fi
fi

echo "Creating backup of Grace data..."

# Backup data directory
echo "Backing up data directory..."
tar -czf $BACKUP_FILE ./data

# Backup environment configuration
echo "Backing up configuration files..."
tar -rf $BACKUP_FILE ./deployment/.env.production
tar -rf $BACKUP_FILE ./deployment/nitter.conf

# Compress the final archive
gzip -f $BACKUP_FILE

echo "Backup completed successfully!"
echo "Backup saved to: $BACKUP_FILE"

exit 0
