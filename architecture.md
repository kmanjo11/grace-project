# Grace Architecture Design

## Overview
Grace is a crypto trading application built on top of Open Interpreter that allows users to trade cryptocurrencies using both Phantom wallet connections and internal system wallets. The application features a sophisticated memory system, user profiles, and advanced trading capabilities.

## Core Components

### 1. Base Open Interpreter Integration
- Extend the OpenInterpreter class to create GraceInterpreter
- Maintain full code execution and system access capabilities
- Add one-time disclosure about system capabilities after sign-in

### 2. Memory Architecture
- **Core Memory**: Bridge new information to existing knowledge
  - Connect new data to already known entities/concepts
  - Enable natural recall in future conversations
- **User-Specific Memory**: Personal memory collections for each user
  - User-taught information stays in their personal memory space
  - Isolated from other users' data
- **Global Memory**: Shared knowledge base accessible to all users
  - Restricted access for updates (only authorized users)
  - Command-based updates (!grace.learn)
  - Topic-based organization with dynamic routing
  - Metadata tracking (timestamps, authors, entry counts)
- **Chroma DB Integration**: Vector database for efficient storage and retrieval
  - Store all new memory (both personal and global)
  - Enable semantic search capabilities

### 3. User Profile System
- User authentication with multiple options:
  - Username, email, password, phone number
  - Gmail login integration
- Secure profile management with encrypted storage
- Each user gets their own sanitized collection name
- Profile data stored in profiles.json
- SecureDataManager for per-user encrypted storage

### 4. UI Interface
- Simple web interface with:
  - "GRACE" title/header
  - User login/logout functionality
  - Main LLM chat box
  - Phantom wallet integration button
  - Scrollable side panel for conversation history
  - Settings and withdraw buttons

### 5. Crypto Trading Features
- **Phantom Wallet Integration**:
  - Connect to user's Phantom wallet
  - Execute transactions through wallet
  - Monitor wallet balances and transactions
- **Internal Wallet System**:
  - Generate wallets for each user
  - Secure key storage and management
  - Transaction capabilities
- **Liquidity Pool Trading**:
  - Integration with Raydium DEX
  - Manual and automated liquidity pool trading
  - Pool depth monitoring and position size calculation
- **Auto-Trading Features**:
  - Risk-based settings (slider system 0-100)
  - Maximum position size configuration
  - Stop loss and take profit settings
  - Performance metrics tracking

## Technical Architecture

### Backend Components
1. **GraceCore**: Extended Open Interpreter core
   - System message customization
   - Command execution handling
   - Response processing

2. **MemoryManager**:
   - ChromaDBConnector: Interface with Chroma DB
   - MemoryRouter: Direct queries to appropriate memory stores
   - EntityLinker: Connect related information across memory stores

3. **UserManager**:
   - Authentication: Handle user login/registration
   - ProfileStorage: Manage user profiles
   - SecureDataManager: Handle encrypted user data

4. **WalletManager**:
   - PhantomConnector: Interface with Phantom wallet
   - InternalWalletGenerator: Create and manage internal wallets
   - TransactionHandler: Process crypto transactions

5. **TradingEngine**:
   - DexTradeService: Interface with decentralized exchanges
   - AutoTradeManager: Handle automated trading strategies
   - CircuitBreakerService: Implement safety features
   - LiquidityPoolManager: Manage liquidity pool interactions

### Frontend Components
1. **LoginInterface**:
   - Authentication forms
   - User registration
   - Password recovery

2. **MainInterface**:
   - Chat window with Grace
   - Command input
   - Response display
   - Conversation history

3. **WalletInterface**:
   - Wallet connection button
   - Balance display
   - Transaction history
   - Withdraw functionality

4. **SettingsInterface**:
   - User preferences
   - Trading settings
   - Auto-trading configuration

## Data Flow
1. User authenticates through the LoginInterface
2. User interacts with Grace through the MainInterface
3. Grace processes requests through GraceCore
4. Memory queries/updates handled by MemoryManager
5. Trading operations processed by TradingEngine
6. Wallet operations managed by WalletManager

## Security Considerations
- Encrypted storage for user credentials and wallet keys
- Secure API communication for trading operations
- Permission-based access to global memory updates
- One-time disclosure for system capabilities
- Sanitized collection names for user isolation

## Extension Points
- Additional trading platforms beyond Solana
- Enhanced memory visualization tools
- Advanced trading strategy development
- Social trading features
- Performance analytics dashboard
