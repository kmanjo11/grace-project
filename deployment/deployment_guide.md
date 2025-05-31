# Grace Project Deployment Guide

This guide provides detailed instructions for deploying the Grace application in a production environment.

## Prerequisites

Before deploying Grace, ensure you have the following prerequisites installed:

- Docker (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- Git
- Bash shell

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/grace-project.git
cd grace-project
```

### 2. Configure Environment Variables

Edit the `.env.production` file in the `deployment` directory to configure your environment:

```bash
nano deployment/.env.production
```

Important settings to configure:

- `JWT_SECRET`: Set to a secure random string (will be auto-generated if left as default)
- `FERNET_KEY`: Set to a secure Fernet key (will be auto-generated if left as default)
- `SOLANA_RPC_URL`: Your Solana RPC endpoint
- `NITTER_INSTANCE`: URL of your Nitter instance (default: http://nitter:8080)

### 3. Configure Nitter

Edit the `nitter.conf` file in the `deployment` directory:

```bash
nano deployment/nitter.conf
```

Important settings to configure:

- `hmacKey`: Set to a random string (will be auto-generated if left as default)
- `redisPassword`: Set if you're using password authentication for Redis

### 4. Start the Application

Run the start script to deploy the application:

```bash
./deployment/start.sh
```

This script will:
- Generate secure keys if needed
- Create necessary directories
- Set appropriate permissions
- Start the application using Docker Compose

### 5. Verify Deployment

After starting the application, verify that all services are running:

```bash
docker ps
```

You should see the following containers running:
- `grace-app`: The main Grace application
- `grace-redis`: Redis for caching and session management
- `grace-nitter`: Nitter instance for social media data

Access the web interface at: `http://your-server-ip:8000`

## Maintenance Operations

### Stopping the Application

To stop the Grace application:

```bash
./deployment/stop.sh
```

### Backing Up Data

To create a backup of all Grace data:

```bash
./deployment/backup.sh
```

Backups are stored in the `backups` directory with timestamps.

### Restoring from Backup

To restore from a backup:

```bash
./deployment/restore.sh backups/grace_backup_20250426_120000.tar.gz
```

Replace the filename with your actual backup file.

### Running Integration Tests

To verify all components are working correctly:

```bash
./deployment/test_integration.sh
```

## Monitoring and Logging

### Viewing Logs

To view logs from all services:

```bash
docker-compose -f deployment/docker-compose.yml logs -f
```

To view logs from a specific service:

```bash
docker-compose -f deployment/docker-compose.yml logs -f grace-app
```

### Monitoring Resources

Monitor container resource usage:

```bash
docker stats
```

## Scaling and Performance

### Resource Requirements

Minimum recommended resources:
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB SSD

For high-traffic deployments:
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 50GB+ SSD

### Scaling Considerations

The Grace application can be scaled horizontally by:

1. Setting up a load balancer in front of multiple Grace instances
2. Using a shared Redis instance for session management
3. Using a shared database for user profiles and memory storage

## Troubleshooting

### Common Issues

1. **Container fails to start**
   - Check logs: `docker-compose -f deployment/docker-compose.yml logs grace-app`
   - Verify environment variables are set correctly
   - Ensure ports are not already in use

2. **Authentication issues**
   - Verify JWT_SECRET is set correctly
   - Check user profile storage permissions

3. **Nitter connection issues**
   - Verify Nitter container is running
   - Check Nitter configuration
   - Ensure Redis is accessible to Nitter

4. **Memory system errors**
   - Check ChromaDB path exists and has correct permissions
   - Verify disk space is sufficient

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the logs for specific error messages
2. Consult the troubleshooting section in the main documentation
3. Contact the development team with detailed information about your issue

## Security Considerations

### Securing Sensitive Data

- All sensitive configuration should be in `.env.production`
- Never commit `.env.production` to version control
- Use Docker secrets for production deployments
- Regularly rotate JWT_SECRET and FERNET_KEY

### Network Security

- Use a reverse proxy (like Nginx) with SSL termination
- Restrict access to Redis port (6379)
- Use firewall rules to limit access to application ports
- Consider using a VPN for administrative access

## Updating Grace

To update to a new version:

1. Pull the latest code: `git pull`
2. Stop the application: `./deployment/stop.sh`
3. Start the application: `./deployment/start.sh`

For major updates, create a backup before updating:
```bash
./deployment/backup.sh
```

## Conclusion

Following this deployment guide will help you successfully deploy and maintain the Grace application in a production environment. For additional support or feature requests, please contact the development team.
