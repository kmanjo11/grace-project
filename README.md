# Grace Project - README.md

## Overview

Grace is a sophisticated crypto trading application based on Open Interpreter that enables users to trade cryptocurrencies on the Solana blockchain through natural language interactions. It features a three-layer memory system, user profile management, wallet integration, and multi-agent architecture.

## Key Features

- **Natural Language Trading**: Execute trades using conversational commands
- **Memory System**: Three-layer architecture for context-aware interactions
- **User Profiles**: Secure authentication and profile management
- **Wallet Integration**: Support for both internal and Phantom wallets
- **Social Media Integration**: Track community sentiment via Nitter
- **Multi-Agent System**: Specialized agents for different tasks
- **Transaction Confirmation**: Secure two-step confirmation process

## Project Structure

```
grace_project/
├── deployment/              # Deployment scripts and configuration
│   ├── Dockerfile           # Container definition
│   ├── docker-compose.yml   # Multi-container setup
│   ├── .env.production      # Production environment variables
│   ├── nitter.conf          # Nitter configuration
│   ├── start.sh             # Application startup script
│   ├── stop.sh              # Application shutdown script
│   ├── backup.sh            # Data backup script
│   ├── restore.sh           # Data restore script
│   ├── test_integration.sh  # Integration testing script
│   └── deployment_guide.md  # Detailed deployment instructions
├── src/                     # Source code
│   ├── agent_framework.py   # Agent framework implementation
│   ├── config.py            # Configuration management
│   ├── crypto_data_service.py # Crypto data service
│   ├── gmgn_service.py      # GMGN API integration
│   ├── grace_core.py        # Core application logic
│   ├── integration_test.py  # Integration tests
│   ├── memory_system.py     # Memory system implementation
│   ├── mock_solana.py       # Solana mock for testing
│   ├── multi_agent_system.py # Multi-agent system
│   ├── nitter_service.py    # Nitter integration
│   ├── password_recovery.py # Password recovery system
│   ├── solana_wallet.py     # Solana wallet management
│   ├── transaction_confirmation.py # Transaction confirmation
│   ├── user_profile.py      # User profile management
│   ├── wallet_connection.py # Wallet connection management
│   └── ui/                  # User interface
│       ├── index.html       # Main HTML file
│       ├── styles.css       # CSS styles
│       └── app.js           # JavaScript application
├── documentation.md         # Comprehensive documentation
├── requirements.txt         # Python dependencies
├── setup.sh                 # Environment setup script
└── updated_todo.md          # Updated task list
```

## Getting Started

### Development Setup

1. Clone the repository
2. Run the setup script:
   ```bash
   ./setup.sh
   ```
3. Start Grace in development mode:
   ```bash
   python src/grace_core.py
   ```

### Production Deployment

For production deployment, follow the instructions in the [Deployment Guide](/deployment/deployment_guide.md).

1. Configure environment variables in `deployment/.env.production`
2. Start the application:
   ```bash
   ./deployment/start.sh
   ```

## Documentation

- [Main Documentation](documentation.md): Comprehensive guide to Grace
- [Deployment Guide](deployment/deployment_guide.md): Production deployment instructions
- [Architecture Design](architecture_design.md): Detailed architecture overview

## Testing

Run the integration tests to verify all components work correctly:

```bash
./deployment/test_integration.sh
```

## Security

Grace implements several security measures:
- Encrypted user data storage
- Secure wallet key management
- Two-step transaction confirmation
- JWT-based authentication
- Input validation and sanitization

## License

[Specify license information here]

## Contact

For support or inquiries, please contact the development team.
