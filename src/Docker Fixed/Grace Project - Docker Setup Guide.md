# Grace Project - Docker Setup Guide

This guide provides detailed instructions for setting up and running the Grace project using Docker. The configuration handles both frontend and backend components, ensuring proper dependency resolution and communication between services.

## Files Overview

1. **`src/ui/Dockerfile`**: Builds the frontend React application with proper dependency resolution
2. **`docker-compose.yml`**: Orchestrates all services (frontend, backend, Redis, Mango V3)
3. **`start_fixed_docker.sh`**: Comprehensive startup script that handles all setup steps

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- Git (to clone the repository if you haven't already)

## Quick Start

The easiest way to get started is to use the provided startup script:

```bash
chmod +x start_fixed_docker.sh
./start_fixed_docker.sh
```

This script will:
1. Copy the fixed configuration files to their proper locations
2. Create necessary directories and environment files
3. Build and start all Docker containers
4. Verify that all services are running correctly

## Manual Setup

If you prefer to set up manually, follow these steps:

### 1. Prepare the Environment

Create a `.env` file in the project root with the following content:

```
# Grace Environment Configuration
GRACE_ENV=production
DEBUG=false
LOG_LEVEL=debug
JWT_SECRET=grace_default_jwt_secret
FERNET_KEY=dGhpc19pc19hX3Byb3Blcl8zMl9ieXRlX2Zlcm5ldF9rZXk=
SESSION_EXPIRY=86400
JWT_EXPIRES_IN=86400
CHROMA_DB_PATH=./data/chromadb
PROFILE_DATA_PATH=./data/profiles.json
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=aa07df83-e1ac-4117-b00d-173e94e4fff7
SOLANA_NETWORK=mainnet-beta
GMGN_API_URL=https://gmgn.ai/defi/router/v1/sol/tx/get_swap_route
GMGN_CHART_URL=https://www.gmgn.cc/kline
PHANTOM_APP_URL=https://phantom.app
PHANTOM_CALLBACK_PATH=/auth/phantom/callback
PHANTOM_DEEP_LINK=https://phantom.app/ul/v1/
PHANTOM_SESSION_PREFIX=phantom_session:
PHANTOM_WALLET_PREFIX=phantom_wallet:
PHANTOM_ENCRYPTION_PRIVATE_KEY=D7i7hHSJvx64bRQv1nD237nf8Z3WH8AoGmAv7ckX16jL
PHANTOM_ENCRYPTION_PUBLIC_KEY=421MrWonHu6VxRAAqYJwEPzACTBLGoeurehPMSKhRzZM
PHANTOM_SESSION_TTL=86400
PHANTOM_RATE_LIMIT=60
SHORT_TERM_MEMORY_SIZE=10
MEDIUM_TERM_MEMORY_EXPIRY=2592000
MEMORY_THRESHOLD=0.7
OPENAI_API_KEY=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
MANGO_V3_BASE_URL=http://mango-v3-service:8080
MANGO_V3_PRIVATE_KEY_PATH=/app/keys/mango_private_key.pem
REACT_APP_BIRDEYE_API_KEY=11a2b1de83784e46986d67b3e71c99ed
REACT_APP_API_URL=/api
```

Create necessary directories:

```bash
mkdir -p data/chromadb
mkdir -p keys
```

### 2. Build and Start the Containers

```bash
# Build the containers
docker-compose build

# Start the containers
docker-compose up -d
```

### 3. Verify Services

Check if all services are running:

```bash
docker-compose ps
```

You should see all services (frontend, backend, redis, mango-v3-service) in the "Up" state.

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:9000

## Troubleshooting

### View Logs

To view logs from all services:

```bash
docker-compose logs -f
```

To view logs from a specific service:

```bash
docker-compose logs -f frontend
docker-compose logs -f backend
```

### Restart Services

If you need to restart a specific service:

```bash
docker-compose restart frontend
docker-compose restart backend
```

### Rebuild After Code Changes

If you make changes to the code:

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## Key Features of This Docker Setup

1. **Symlink for Dependencies**: The frontend Dockerfile creates a symlink for axios in the services directory, resolving import issues between directories.

2. **Multi-stage Builds**: Both frontend and backend use multi-stage builds to optimize image size.

3. **Health Checks**: All services include health checks to ensure proper startup and monitoring.

4. **Environment Variables**: Standardized environment variables across all services.

5. **Volume Mounting**: Proper volume mounting for data persistence.

## Understanding the Docker Architecture

The Docker setup consists of four main services:

1. **Frontend (React)**: Serves the UI on port 3000, built with Vite and React.

2. **Backend (Python)**: Runs the API server on port 9000, built with Quart/Flask.

3. **Redis**: Provides caching and session storage for the backend.

4. **Mango V3 Service**: Placeholder service for Mango V3 integration.

The services communicate through an internal Docker network, with the frontend proxying API requests to the backend.

## Stopping the Application

To stop all services:

```bash
docker-compose down
```

To stop and remove all data volumes:

```bash
docker-compose down -v
```

## Advanced Configuration

### Customizing Environment Variables

Edit the `.env` file to customize environment variables.

### Development Mode

For development with hot-reloading:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Production Deployment

For production deployment, consider adding SSL/TLS termination with a reverse proxy like Nginx or Traefik in front of the stack.
