# Grace Project Docker Guide

> Note: For canonical run/setup instructions (ports 9000/3000, env export, dev flow), see `RUNBOOK.md` at the repo root. This document serves as a Docker-specific reference. If any conflicts arise, `RUNBOOK.md` takes precedence.

This guide explains how to run the Grace project using Docker, which provides an isolated environment with all dependencies pre-configured.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- OpenAI API key (for AI functionality)

## Quick Start

1. Extract the Grace project files to a directory of your choice
2. Navigate to the project directory
3. Run the start script:
   ```bash
   chmod +x deployment/start_docker.sh
   ./deployment/start_docker.sh
   ```
4. Access the Grace UI at: http://localhost:9000

## Configuration

The first time you run the start script, it will create a `.env` file with default values. Edit this file to configure:

- OpenAI API key (required for AI functionality)
- JWT secret for authentication
- Solana RPC URL
- Other environment variables

## Docker Management Scripts

The Grace project includes several scripts to manage the Docker environment:

### Start Docker Environment

```bash
./deployment/start_docker.sh
```

This script:
- Creates a default `.env` file if one doesn't exist
- Builds and starts all Docker containers
- Verifies that all containers are running
- Provides the URL to access the Grace UI

### Stop Docker Environment

```bash
./deployment/stop_docker.sh
```

This script stops all Docker containers for the Grace project.

### Test Docker Deployment

```bash
./deployment/test_docker.sh
```

This script:
- Builds the Docker images
- Starts the containers
- Tests the API and UI connections
- Checks for the enterprise module error
- Stops the containers

Use this script to verify that your Docker environment is working correctly.

## Docker Components

The Grace Docker environment consists of three containers:

1. **grace-app**: The main Grace application
2. **grace-redis**: Redis for caching and session management
3. **grace-nitter**: Nitter instance for social media data

## Data Persistence

All data is stored in Docker volumes:
- `grace-data`: Contains user profiles, memory data, and other application data
- `grace-redis-data`: Contains Redis data

These volumes persist even when containers are stopped, ensuring your data is not lost.

## Troubleshooting

If you encounter issues:

1. Check container logs:
   ```bash
   docker logs grace-app
   ```

2. Verify all containers are running:
   ```bash
   docker-compose -f deployment/docker-compose.yml ps
   ```

3. Restart the environment:
   ```bash
   ./deployment/stop_docker.sh
   ./deployment/start_docker.sh
   ```

## Advanced Configuration

To modify the Docker configuration:

- Edit `deployment/docker-compose.yml` for container settings
- Edit `deployment/Dockerfile` for application build process
- Edit `deployment/nitter.conf` for Nitter configuration

## Security Notes

- The default configuration is suitable for local development
- For production deployment, ensure you set secure values for JWT_SECRET and FERNET_KEY
- Never share your OpenAI API key or other sensitive information
