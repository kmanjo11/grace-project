#!/bin/bash
# Script to build and start the Grace project with fixed Docker configuration

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Grace Project Docker Startup Script ===${NC}"
echo -e "${YELLOW}This script will build and start the Grace project using the fixed Docker configuration${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Copy fixed files to their proper locations
echo -e "${YELLOW}Copying fixed configuration files...${NC}"

# Copy frontend Dockerfile
if [ -f "src/ui/Dockerfile.fixed" ]; then
    cp src/ui/Dockerfile.fixed src/ui/Dockerfile
    echo -e "${GREEN}✓ Frontend Dockerfile updated${NC}"
else
    echo -e "${RED}× Frontend Dockerfile.fixed not found${NC}"
    exit 1
fi

# Copy docker-compose.yml
if [ -f "docker-compose.yml.fixed" ]; then
    cp docker-compose.yml.fixed docker-compose.yml
    echo -e "${GREEN}✓ docker-compose.yml updated${NC}"
else
    echo -e "${RED}× docker-compose.yml.fixed not found${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file with default values...${NC}"
    cat > .env << EOL
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
EOL
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Create data and keys directories if they don't exist
mkdir -p data/chromadb
mkdir -p keys
echo -e "${GREEN}✓ Data directories created${NC}"

# Stop any running containers
echo -e "${YELLOW}Stopping any running containers...${NC}"
docker-compose down

# Build and start the containers
echo -e "${YELLOW}Building and starting containers...${NC}"
docker-compose build
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Docker build failed. Please check the error messages above.${NC}"
    exit 1
fi

docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Docker Compose up failed. Please check the error messages above.${NC}"
    exit 1
fi

# Check if containers are running
echo -e "${YELLOW}Checking container status...${NC}"
sleep 5
RUNNING_CONTAINERS=$(docker-compose ps --services --filter "status=running" | wc -l)
EXPECTED_CONTAINERS=4 # frontend, backend, redis, mango-v3-service

if [ "$RUNNING_CONTAINERS" -eq "$EXPECTED_CONTAINERS" ]; then
    echo -e "${GREEN}✓ All containers are running successfully!${NC}"
else
    echo -e "${RED}× Some containers failed to start. Expected $EXPECTED_CONTAINERS but found $RUNNING_CONTAINERS running.${NC}"
    docker-compose ps
    exit 1
fi

# Print access information
echo -e "\n${GREEN}=== Grace Project is now running! ===${NC}"
echo -e "Access the application at:"
echo -e "  Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "  Backend API: ${YELLOW}http://localhost:8000${NC}"
echo -e "\nTo view logs:"
echo -e "  ${YELLOW}docker-compose logs -f${NC}"
echo -e "\nTo stop the application:"
echo -e "  ${YELLOW}docker-compose down${NC}"
