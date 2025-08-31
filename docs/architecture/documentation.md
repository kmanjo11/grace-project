# Grace Project Documentation

> Operational run/setup instructions are consolidated in the root `RUNBOOK.md` (canonical). This document focuses on background/architecture. If any conflicts arise, follow `RUNBOOK.md`.

## Overview

Grace is a crypto trading application based on Open Interpreter that enables users to trade cryptocurrencies on the Solana blockchain. It features a sophisticated memory system, user profile management, wallet integration, and natural language processing capabilities.

## Architecture

Grace follows a modular architecture with the following key components:

1. **User Profile System**: Manages user authentication, data storage, and wallet connections
2. **Memory System**: Provides a three-layer memory architecture for context management
3. **API Services**: Integrates with external services for social media data and trading
4. **Wallet Integration**: Supports both internal wallets and Phantom wallet connections
5. **Transaction Confirmation**: Ensures secure transaction execution with explicit user approval
6. **Natural Language Processing**: Enables command processing through natural language
7. **Multi-Agent System**: Provides specialized agents for different tasks within Grace

## Components

### User Profile System

The User Profile System manages user accounts, authentication, and secure data storage.

**Key Features:**
- User registration with username, email, password, and phone number
- Secure authentication with password hashing
- JWT token generation for sessions
- Email-based password recovery
- Profile data encryption using Fernet
- Special authorization for admin users

**Implementation Files:**
- `/src/user_profile.py`: Core user profile functionality
- `/src/password_recovery.py`: Password recovery system

### Memory System

The Memory System provides a three-layer architecture for storing and retrieving information.

**Key Features:**
- Short-term memory: Active context window for immediate conversations
- Medium-term memory: Personal user memories that persist across sessions
- Long-term memory: Global shared knowledge accessible to all users
- Time-based memory decay for automatic pruning
- Priority-based retrieval with relevance scoring
- Entity extraction and relationship tracking
- Memory merging for related information

**Implementation Files:**
- `/src/memory_system.py`: Core memory system functionality

### API Services

Grace integrates with external APIs to provide social media data and trading functionality.

#### Nitter Service

The Nitter Service provides access to Twitter data through a self-hosted Nitter instance.

**Key Features:**
- Community seeds functionality for tracking influential accounts
- Pulse tracking for topics and sentiment
- Auto-discovery for community changes
- Smart caching to reduce API calls
- Association with memory system entities

**Implementation Files:**
- `/src/nitter_service.py`: Nitter integration using NTscraper

#### GMGN Service

The GMGN Service enables trading on the Solana blockchain through the GMGN API.

**Key Features:**
- Token price and chart data retrieval
- Market information retrieval
- Trade execution with confirmation flow
- Token swapping with confirmation flow
- Wallet balance retrieval

**Implementation Files:**
- `/src/gmgn_service.py`: GMGN API integration

### Wallet Integration

Grace supports both internal wallets and Phantom wallet connections for trading.

**Key Features:**
- Internal wallet generation and management
- Phantom wallet connection flow
- Balance retrieval and monitoring
- Transaction signing and execution
- Unified interface for both wallet types

**Implementation Files:**
- `/src/solana_wallet.py`: Solana wallet management
- `/src/wallet_connection.py`: Wallet connection management

### Transaction Confirmation

The Transaction Confirmation System ensures secure transaction execution with explicit user approval.

**Key Features:**
- Two-step confirmation process
- Transaction preparation and validation
- Explicit user confirmation requirement
- Transaction cancellation
- Natural language processing for transaction commands

**Implementation Files:**
- `/src/transaction_confirmation.py`: Transaction confirmation system

### Agent Framework

The Agent Framework provides specialized agents for different tasks within Grace.

**Key Features:**
- BaseAgent foundation for common functionality
- SmartRouter for task routing
- Specialized agents for different domains
- Agent coordination through EnhancedAgentManager

**Implementation Files:**
- `/src/agent_framework.py`: Agent framework implementation
- `/src/multi_agent_system.py`: Multi-agent system implementation

## API Integrations

### Nitter/NTscraper

Grace uses NTscraper to interact with a self-hosted Nitter instance for Twitter data.

**Configuration:**
- Nitter Instance URL: http://localhost:8085 (configurable)
- No authentication required for local instance

**Usage Example:**
```python
from src.nitter_service import NitterService

nitter = NitterService(nitter_instance="http://localhost:8085")
results = nitter.search_twitter(query="solana", count=10)
```

### GMGN Solana Trading API

Grace uses the GMGN API for trading on the Solana blockchain.

**Configuration:**
- API Endpoint: https://gmgn.ai/defi/router/v1/sol/tx/get_swap_route
- No API key required

**Usage Example:**
```python
from src.gmgn_service import GMGNService

gmgn = GMGNService()
price = gmgn.get_token_price(token="So11111111111111111111111111111111111111112", chain="sol")
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Solana CLI tools (optional, for advanced wallet operations)
- Self-hosted Nitter instance (for social media functionality)
- Docker and Docker Compose (for production deployment)

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/grace-project.git
cd grace-project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
export SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=aa07df83-e1ac-4117-b00d-173e94e4fff7
export SOLANA_NETWORK=mainnet-beta
```

4. Initialize the application:
```bash
python src/grace_core.py
```

### Production Deployment

For production deployment, Grace provides a comprehensive Docker-based deployment system. See the [Deployment Guide](/deployment/deployment_guide.md) for detailed instructions on:

- Setting up the production environment
- Configuring environment variables
- Starting and stopping the application
- Backing up and restoring data
- Monitoring and logging
- Scaling and performance optimization
- Troubleshooting common issues
- Security considerations
- Updating procedures

## Usage

### User Management

```python
# Create a new user
user = grace.create_user(username="john_doe", email="john@example.com", password="secure_password")

# Authenticate a user
auth_result = grace.authenticate_user(username="john_doe", password="secure_password")

# Update user profile
grace.update_user_profile(user_id="john_doe", data={"phone": "123-456-7890"})
```

### Wallet Operations

```python
# Generate internal wallet
wallet = grace.generate_internal_wallet(user_id="john_doe")

# Connect Phantom wallet
phantom = grace.connect_phantom_wallet(user_id="john_doe", wallet_address="your_phantom_address")

# Check wallet balance
balance = grace.get_wallet_balance(user_id="john_doe")
```

### Trading Operations

```python
# Prepare a swap transaction
tx = grace.prepare_transaction(
    user_id="john_doe",
    transaction_type="swap",
    parameters={
        "from_token": "So11111111111111111111111111111111111111112",  # SOL
        "to_token": "7EYnhQoR9YM3N7UoaKRoA44Uy8JeaZV3qyouov87awMs",  # Example token
        "amount": "0.1"
    }
)

# Confirm the transaction
result = grace.confirm_transaction(user_id="john_doe", confirmation_id=tx["confirmation_id"])
```

### Natural Language Commands

Grace supports natural language commands for various operations:

- **Wallet Operations**: "Show my wallet balance", "Check my portfolio"
- **Price Queries**: "What's the price of Solana?", "Show me SOL price chart"
- **Trading**: "Buy 0.1 SOL", "Swap 0.5 SOL to BONK"
- **Transaction Management**: "List pending transactions", "Confirm transaction xyz123"
- **Social Media**: "What's trending about Solana?", "Show latest tweets about crypto"

## Security Considerations

1. **User Data Protection**:
   - All sensitive user data is encrypted using Fernet encryption
   - Passwords are hashed and never stored in plaintext
   - JWT tokens are used for session management with appropriate expiration

2. **Wallet Security**:
   - Private keys for internal wallets are encrypted
   - Phantom wallet integration uses secure connection methods
   - No private keys are transmitted over the network

3. **Transaction Security**:
   - Two-step confirmation process for all financial transactions
   - Explicit user approval required before execution
   - Transaction timeout to prevent delayed execution attacks

4. **API Security**:
   - Rate limiting to prevent abuse
   - Input validation for all API calls
   - Error handling to prevent information leakage

5. **Deployment Security**:
   - Docker containerization for isolation
   - Environment variable management for sensitive data
   - Secure key generation and rotation
   - Network security recommendations in deployment guide

## Testing

Grace includes comprehensive testing to ensure all components work correctly:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test components working together
3. **End-to-End Tests**: Test the entire application flow

To run the tests:

```bash
# Run unit tests
python -m unittest discover -s tests/unit

# Run integration tests
python src/integration_test.py

# Run comprehensive tests
python src/comprehensive_testing.py

# Run deployment integration tests
./deployment/test_integration.sh
```

## Extending Grace

Grace is designed to be extensible. Here are some ways to extend its functionality:

1. **Add New API Integrations**:
   - Create a new service class in `/src/`
   - Implement the required methods
   - Update the agent framework to use the new service

2. **Add New Wallet Types**:
   - Extend the wallet manager in `/src/solana_wallet.py`
   - Implement the required methods for the new wallet type
   - Update the user profile system to support the new wallet type

3. **Enhance Memory System**:
   - Add new memory layers in `/src/memory_system.py`
   - Implement new retrieval methods
   - Update the memory bridging system

4. **Add New Agent Types**:
   - Create a new agent class in `/src/multi_agent_system.py`
   - Implement the required methods
   - Update the agent router to use the new agent

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Check username and password
   - Verify JWT token expiration
   - Check for encryption key issues

2. **Wallet Connection Issues**:
   - Verify Solana RPC URL is accessible
   - Check wallet address format
   - Ensure sufficient SOL balance for operations

3. **API Integration Issues**:
   - Verify Nitter instance is running
   - Check GMGN API endpoint accessibility
   - Verify network connectivity

4. **Deployment Issues**:
   - See the [Deployment Guide](/deployment/deployment_guide.md) for detailed troubleshooting
   - Check Docker and Docker Compose installation
   - Verify environment variables are set correctly
   - Check container logs for specific error messages

### Logging

Grace uses Python's logging module for detailed logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Logs are stored in `/logs/grace.log` by default.

In production deployment, logs can be accessed using:

```bash
docker-compose -f deployment/docker-compose.yml logs -f grace-app
```

## Maintenance

Regular maintenance tasks for Grace include:

1. **Backup Data**:
   - Use the provided backup script: `./deployment/backup.sh`
   - Store backups securely off-site
   - Test restore procedure periodically

2. **Update Dependencies**:
   - Check for security updates regularly
   - Update Python packages with `pip install --upgrade -r requirements.txt`
   - Update Docker images with `docker-compose pull`

3. **Monitor Performance**:
   - Check resource usage with `docker stats`
   - Monitor API response times
   - Review logs for errors or warnings

4. **Security Audits**:
   - Regularly rotate JWT_SECRET and FERNET_KEY
   - Review access logs for suspicious activity
   - Update SSL certificates before expiration

## Conclusion

Grace provides a powerful platform for crypto trading on the Solana blockchain with natural language capabilities. Its modular architecture allows for easy extension and customization, while its security features ensure safe operation with user funds.

The comprehensive deployment system makes it easy to deploy and maintain Grace in a production environment, with tools for monitoring, backup, and scaling.

For additional support or feature requests, please contact the development team.
