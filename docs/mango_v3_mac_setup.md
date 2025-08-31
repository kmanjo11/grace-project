# Mango V3 Setup Guide for Mac

This document explains how the Mango V3 client is integrated into the Grace project and provides instructions for setting it up on a Mac system.

## Architecture Overview

The Grace project integrates with Mango V3 through three main components:

1. **Docker Service**: Mango V3 runs as a separate container exposing an API on port 8080
2. **Python Extension**: Backend communicates with Mango V3 through `src/mango_v3_extension.py`
3. **Frontend Integration**: Optional direct integration using the npm package

## Setup Instructions for Mac

### Step 1: Clone the Repository

ONLY IF YOU HAVEN'T ALREADY:

```bash
git clone [your-repo-url] grace_project
cd grace_project
```

### Step 2: Set Up the Mango V3 Docker Service

There are two ways to get the Mango V3 service image:

#### Option A: Build the image yourself

```bash
docker build -t mango-v3-service:latest -f deployment/mango-v3.Dockerfile .
```

#### Option B: Pull a pre-built image (if available)

```bash
docker pull [registry]/mango-v3-service:latest
```

### Step 3: Configure Environment Variables

Create or edit your `.env` file to include:

```
# Mango V3 Configuration
MANGO_V3_BASE_URL=http://mango_v3_service:8080
MANGO_V3_PRIVATE_KEY_PATH=/app/keys/mango_private_key.pem
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WS_URL=wss://api.mainnet-beta.solana.com
```

### Step 4: Start the Services

Use Docker Compose to launch both the Grace backend and Mango V3 service:

```bash
docker-compose up -d
```

The required directories (`mango_v3_config` and `data/mango`) will be created automatically as bind mounts.

### Step 5: Frontend Setup (if needed)

For direct frontend integration with Mango V3:

```bash
cd src/ui
npm install @blockworks-foundation/mango-client
```

### Step 6: Verify the Setup

Check if the services are running:

```bash
docker ps
```

You should see both `grace-backend` and `mango-v3-service` containers running.

To check the logs:

```bash
docker logs mango-v3-service
```

## Additional Resources

- **Mango V3 Client Documentation**: https://blockworks-foundation.github.io/mango-client-v3/
- **Internal Implementation**: `src/mango_v3_extension.py` contains the Python interface
- **Docker Configuration**: See `docker-compose.yml` for service configuration

## REST API vs npm Client Package

The Grace project utilizes two different methods to access Mango V3 functionality:

1. **REST API (Backend Usage)**
   - Used by the Python extension (`mango_v3_extension.py`) for backend operations
   - Accessed via HTTP requests to the Docker service endpoint
   - Contains endpoints like `GET /api/markets/{market_name}/candles` for OHLCV chart data
   - Parameters for chart endpoint include:
     - `resolution`: Candle resolution in seconds (default: 60)
     - `start_time`: Optional start time filter
     - `end_time`: Optional end time filter

2. **npm Client Package (Frontend Usage)**
   - `@blockworks-foundation/mango-client` used for direct frontend interactions
   - Provides JavaScript/TypeScript functions instead of REST endpoints
   - Offers convenient frontend integration with libraries like TradingView Lightweight Charts
   - May contain additional client-side utilities not available in REST API

### Which to Use When

- **Backend Operations**: Always use the REST API via Python extension
- **Frontend Development**: You can choose between:
  - Making API calls to your backend which then forwards to the Mango API
  - Using the npm package directly for frontend-to-Mango communication

### Charting Capabilities

Both interfaces provide access to the same core market data, but with different implementation approaches:
- REST API provides raw candle data that needs custom rendering
- npm client may include additional utilities for direct chart integration

## Private Key Handling for Solana Signing

The Grace project uses a specific approach to handle private keys for Solana transactions with Mango V3:

### Function and Purpose

This private key serves as a **Solana signing key** that enables transactions on behalf of users:

- It functions as a **service account** that signs Solana transactions required for Mango V3 operations
- When users make trades or other actions, the backend uses this key to sign the necessary transactions
- Users don't need to provide their own Solana keys for basic operations
- The system acts on behalf of users who have authenticated through your application

### Configuration

- The `MANGO_V3_PRIVATE_KEY_PATH` environment variable in your `.env` file specifies where the system looks for the private key file
- Default path is `/app/keys/mango_private_key.pem` inside the container
- The physical key file on your host machine is mapped via Docker volume: `./keys:/app/keys`

### Key Loading Mechanism
   - The `MangoV3Client` class in `mango_v3_extension.py` loads the private key at runtime:
   ```python
   if private_key_path and os.path.exists(private_key_path):
       try:
           with open(private_key_path, "r") as f:
               self.private_key = f.read().strip()
           self.logger.info("Loaded private key for Mango V3 client")
       except Exception as e:
           self.logger.error(f"Failed to load private key: {e}")
   ```

### Setting Up on Mac
- Create a `keys` directory in your project root if it doesn't exist
- Generate or copy your Solana private key to `./keys/mango_private_key.pem`
- Ensure the file permissions are secure (e.g., `chmod 600 ./keys/mango_private_key.pem`)

### Common Issues & Solutions
- If you encounter Helius or other Solana service errors about missing private keys, check:
  - The key file exists in the correct location
  - The path in `.env` matches where Docker mounts it
  - The key file has the correct format (PEM for this project)
  - File permissions allow the container to read the file

### Security Best Practices
- Never commit private keys to version control
- Manage your `.env` file securely
- Consider using a key management service for production deployments

## Notes on Mango V3 REST API Source

The Mango V3 REST API used in this project appears to be sourced from an external repository or container registry. While the specific source isn't explicitly documented in the project, here's how to approach working with it:

1. **Understanding the Black Box Approach**:
   - Your system interacts with the Mango V3 REST API as a containerized service
   - The Python extension (`mango_v3_extension.py`) abstracts all API calls to this service
   - This architecture allows you to treat the REST API as a "black box" - you don't need to know its internal implementation

2. **Options When Missing the Source**:
   - Check if a pre-built image exists in your organization's registry (likely `mango-v3-service:latest`)
   - Look for the image on Docker Hub or GitHub Container Registry under the Blockworks Foundation organization
   - Consider reaching out to the original developers for the source or Docker image
   - Inspect the API endpoints by reviewing the `mango_v3_extension.py` file and implement a compatible service

3. **Potential Sources**:
   - The official Mango Markets repositories:
     - https://github.com/blockworks-foundation/mango-v3
     - https://github.com/blockworks-foundation/mango-v3-service
   - Community-maintained forks or adaptations

## General Notes

- The Mango V3 service requires valid Solana RPC and WebSocket URLs
- The `.env` file contains sensitive configuration and should not be committed to version control
- Both REST API and npm client are active in a typical setup, serving different parts of the application



SOURCES:Mango Markets v3 Service on GitHub: Offers a full REST and WebSocket service that you can run locally to mimic a centralized exchange API.
GitHub: https://github.com/microwavedcola1/mango-v3-service
Mango Markets v3 TypeScript Client Library: The official client for interacting with the Mango program.
GitHub: https://github.com/blockworks-foundation/mango-client-v3
Documentation: https://blockworks-foundation.github.io/mango-client-v3/
Mango Markets Documentation: Contains general information about the v3 protocol.
GitHub: https://github.com/blockworks-foundation/mango-docs