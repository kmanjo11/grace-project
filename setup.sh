#!/bin/bash

# Grace Project Setup Script
# This script sets up the Grace project environment

echo "===== Grace Project Setup ====="
echo "Starting setup at $(date)"
echo

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi
python3 --version
echo "Python check: PASSED"
echo

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "Virtual environment created and activated."
echo

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Dependency installation: FAILED"
    exit 1
fi
echo "Dependency installation: PASSED"
echo

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/chromadb
mkdir -p logs
echo "Directories created."
echo

# Set up configuration
echo "Setting up configuration..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Grace Environment Configuration

# Application Settings
GRACE_ENV=development
DEBUG=true
LOG_LEVEL=debug

# Security Settings
JWT_SECRET=$(openssl rand -hex 32)
FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
SESSION_EXPIRY=86400  # 24 hours in seconds

# Database Settings
CHROMA_DB_PATH=./data/chromadb
PROFILE_DATA_PATH=./data/profiles.json

# Solana Settings
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=aa07df83-e1ac-4117-b00d-173e94e4fff7
SOLANA_NETWORK=mainnet-beta

# Nitter Settings
NITTER_INSTANCE=http://localhost:8085

# GMGN API Settings
GMGN_API_URL=https://gmgn.ai/defi/router/v1/sol/tx/get_swap_route
GMGN_CHART_URL=https://www.gmgn.cc/kline

# Phantom Wallet Settings
PHANTOM_APP_URL=https://phantom.app
PHANTOM_CALLBACK_PATH=/auth/phantom/callback
PHANTOM_SESSION_PREFIX=phantom_session:
PHANTOM_WALLET_PREFIX=phantom_wallet:

# Memory System Settings
SHORT_TERM_MEMORY_SIZE=10
MEDIUM_TERM_MEMORY_EXPIRY=2592000  # 30 days in seconds
MEMORY_THRESHOLD=0.7
EOL
fi
echo "Configuration setup: PASSED"
echo

# Make deployment scripts executable
echo "Setting permissions for deployment scripts..."
chmod +x deployment/*.sh
echo "Permissions set."
echo

echo "===== Setup Summary ====="
echo "Grace project setup completed successfully!"
echo "To start Grace in development mode, run:"
echo "  python src/grace_core.py"
echo
echo "To deploy Grace in production, see:"
echo "  deployment/deployment_guide.md"
echo
echo "Completed at $(date)"
echo "=================================="

exit 0
