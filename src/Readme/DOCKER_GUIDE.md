# Grace Project - Docker Setup Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Services Overview](#services-overview)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)
- [CI/CD Integration](#cicd-integration)

## Prerequisites

### System Requirements
- Docker 20.10.0+
- Docker Compose 2.0.0+
- 4GB RAM (8GB recommended)
- 10GB free disk space

### Required Ports
- 3000: Frontend development server
- 9000: Backend API
- 8080: Mango V3 Service
- 80/443: Nginx (production)

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd grace_project
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Update the `.env` file with your configuration.

4. Start the services:
   ```bash
   docker-compose up -d
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:9000
   - API Docs: http://localhost:9000/docs

## Development Setup

### Starting Development Environment
```bash
# Start all services in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f

# Run tests
docker-compose exec backend pytest
```

### Frontend Development
- Uses Vite with hot module replacement
- Source code is mounted as a volume for live updates
- Accessible at http://localhost:3000

### Backend Development
- Automatic reload on code changes
- Debugger configured on port 5678
- Access API docs at http://localhost:9000/docs

## Production Deployment

### Building Production Images
```bash
# Build all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start in detached mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Updating Services
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

## Services Overview

### Backend Service
- **Port**: 9000
- **Image**: Custom Python 3.10
- **Features**:
  - FastAPI application
  - JWT authentication
  - Database migrations
  - Async task processing

### Frontend Service
- **Port**: 3000 (dev), 80 (prod)
- **Image**: Node.js 18 + Nginx
- **Features**:
  - React + TypeScript
  - Vite build system
  - Production-optimized Nginx config

### Mango V3 Service
- **Port**: 8080
- **Image**: Custom Solana integration
- **Features**:
  - Solana RPC connection
  - Mango Markets V3 integration
  - Caching layer

## Environment Configuration

### Required Variables
```env
# Backend
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@db:5432/grace
REDIS_URL=redis://redis:6379/0

# Solana
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WS_URL=wss://api.mainnet-beta.solana.com

# Mango V3
MANGO_V3_BASE_URL=http://mango_v3_service:8080
```

### Optional Variables
```env
# Logging
LOG_LEVEL=info
DEBUG=false

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:9000

# Rate Limiting
RATE_LIMIT=100/minute
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Find processes using a port
sudo lsof -i :9000

# Kill process
kill -9 <PID>
```

#### 2. Docker Build Failures
```bash
# Clean build
sudo docker system prune -a
sudo docker-compose build --no-cache
```

#### 3. Database Issues
```bash
# Reset database
sudo docker-compose down -v
sudo docker-compose up -d db
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Follow logs with timestamps
docker-compose logs -f --tail=100 --timestamps
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: yourusername/grace:latest
```

## Maintenance

### Updating Dependencies
```bash
# Backend
sudo docker-compose exec backend poetry update

# Frontend
sudo docker-compose exec frontend pnpm update
```

### Database Backups
```bash
# Create backup
docker exec -t postgres pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y_%H_%M_%S`.sql

# Restore backup
cat your_dump.sql | docker exec -i postgres psql -U postgres
```

## Security Considerations

1. **Secrets Management**
   - Never commit `.env` files
   - Use Docker secrets in production
   - Rotate API keys regularly

2. **Network Security**
   - Use internal Docker networks
   - Configure proper CORS
   - Enable HTTPS in production

3. **Monitoring**
   - Set up log aggregation
   - Monitor container resources
   - Configure alerts for failures

## Support

For additional help, please contact:
- **Email**: support@graceproject.com
- **Slack**: #grace-support
- **Documentation**: [Grace Docs](https://docs.graceproject.org)

---
Last Updated: 2025-05-29
