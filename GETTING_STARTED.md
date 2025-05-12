# Getting Started with Grace Trading System

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.9 or higher
- Node.js 16 or higher
- Docker and Docker Compose (for containerized deployment)
- Git

## Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/kmanjo11/grace-trading-system.git
   cd grace-trading-system
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set Up Frontend Dependencies**
   ```bash
   cd src/ui
   npm install
   ```

4. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Update the following values in `.env`:
     - `SOLANA_RPC_URL`: Your Solana RPC endpoint
     - `JWT_SECRET_KEY`: Generate a secure random key
     - `ADMIN_PASSWORD`: Set your admin password

5. **Start the Development Server**
   ```bash
   # Start backend (from project root)
   python src/api_server.py

   # Start frontend (in src/ui directory)
   npm run dev
   ```

6. **Access the Application**
   - Backend API: http://localhost:5000
   - Frontend UI: http://localhost:3000

## Development Setup

### Backend Development
1. Install additional development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   python -m pytest tests/
   ```

3. Start the development server with hot reload:
   ```bash
   python src/api_server.py --debug
   ```

### Frontend Development
1. Install development tools:
   ```bash
   cd src/ui
   npm install -D @types/react @types/node
   ```

2. Start development server with hot reload:
   ```bash
   npm run dev
   ```

3. Run tests:
   ```bash
   npm test
   ```

## Docker Deployment

1. Build and start containers:
   ```bash
   docker-compose up -d
   ```

2. View logs:
   ```bash
   docker-compose logs -f
   ```

3. Stop containers:
   ```bash
   docker-compose down
   ```

## Common Issues and Solutions

### Backend Issues
1. **Database Connection Errors**
   - Check if the database container is running
   - Verify database credentials in `.env`

2. **API Errors**
   - Ensure all required environment variables are set
   - Check logs for detailed error messages

### Frontend Issues
1. **Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Update dependencies: `npm update`

2. **Connection Issues**
   - Verify API URL in frontend configuration
   - Check CORS settings in backend

## Additional Resources

- [API Documentation](./docs/API.md)
- [Deployment Guide](./deployment/deployment_guide.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
- [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)

## Support

For support:
1. Check the [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)
2. Search existing [GitHub Issues](https://github.com/kmanjo11/grace-trading-system/issues)
3. Create a new issue if your problem persists
