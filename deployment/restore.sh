#!/bin/bash

# Grace Project Restore Script
# This script restores a backup of the Grace application data

# Set the working directory to the project root
cd "$(dirname "$0")/.."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required to restore Grace data."
    echo "Please install Docker before continuing."
    exit 1
fi

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Error: No backup file specified."
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -1 ./backups/*.tar.gz 2>/dev/null || echo "No backups found in ./backups/"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Check if the application is running
if [ ! -z "$(docker ps -q -f name=grace-app)" ]; then
    echo "Warning: Grace application is currently running."
    echo "It is recommended to stop the application before restoring a backup."
    read -p "Stop the application before continuing? (Y/n): " stop_app
    if [[ ! "$stop_app" =~ ^[Nn]$ ]]; then
        echo "Stopping Grace application..."
        ./deployment/stop.sh
    fi
fi

echo "Restoring backup from: $BACKUP_FILE"

# Create temporary directory for extraction
TEMP_DIR="./temp_restore"
mkdir -p $TEMP_DIR

# Extract backup
echo "Extracting backup..."
tar -xzf "$BACKUP_FILE" -C $TEMP_DIR

# Restore data directory
echo "Restoring data directory..."
if [ -d "$TEMP_DIR/data" ]; then
    # Create backup of current data if it exists
    if [ -d "./data" ]; then
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        echo "Creating backup of current data..."
        mv ./data "./data_backup_$TIMESTAMP"
    fi
    
    # Move restored data into place
    mv "$TEMP_DIR/data" ./
else
    echo "Warning: No data directory found in backup."
fi

# Restore configuration files
echo "Restoring configuration files..."
if [ -f "$TEMP_DIR/deployment/.env.production" ]; then
    cp "$TEMP_DIR/deployment/.env.production" ./deployment/
else
    echo "Warning: No .env.production file found in backup."
fi

if [ -f "$TEMP_DIR/deployment/nitter.conf" ]; then
    cp "$TEMP_DIR/deployment/nitter.conf" ./deployment/
else
    echo "Warning: No nitter.conf file found in backup."
fi

# Clean up temporary directory
echo "Cleaning up..."
rm -rf $TEMP_DIR

echo "Restore completed successfully!"
echo "You can now start the Grace application with: ./deployment/start.sh"

exit 0
