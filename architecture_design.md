# Grace Architecture Design

## Overview
Grace is a crypto trading application based on Open Interpreter that enables users to trade cryptocurrencies through natural language interactions. The application integrates with various APIs and services to provide a comprehensive trading experience while maintaining a conversational interface.

## Core Components

### 1. Open Interpreter Extension
- **Base Framework**: Extends Open Interpreter's core functionality
- **Synchronous Approach**: Maintains compatibility with Open Interpreter's synchronous code patterns
- **System Message**: Customized to include Grace-specific capabilities and instructions

### 2. Memory System
- **Three-Tiered Architecture**:
  - **Core Memory**: Base knowledge that Grace has about entities and concepts
  - **User-Specific Memory**: Personal memory exclusive to each user
  - **Global Memory**: Shared knowledge accessible to all users
- **Storage**: ChromaDB for vector embeddings and semantic search
- **Entity Linking**: Connects new information to existing knowledge
- **Command-Based Updates**: Authorized users can update global memory using `!grace.learn` command
- **Memory Persistence**: Maintains memories across sessions

### 3. User Profile System
- **Authentication**:
  - Username/password login
  - Email authentication
  - Optional phone number
  - Gmail login option
- **Profile Storage**: Secure, encrypted storage of user profiles
- **Session Management**: JWT token-based session tracking
- **One-Time Disclosure**: Shows system capabilities disclosure after first login

### 4. Conversation Management
- **Context Preservation**: Maintains conversation context across sessions
- **Topic Tracking**: Identifies and tracks conversation topics
- **Entity Extraction**: Identifies entities mentioned in conversations
- **Background Tasks**: Handles data searches and trade facilitation
- **Memory-Augmented Responses**: Enhances responses with relevant memory

### 5. API Integration Framework
- **Dynamic API Selection**: Selects appropriate API based on user intent
- **Context-Aware Routing**: Routes requests to the correct API based on conversation context
- **Integrated APIs**:
  - **Mango Client**: For leverage trading on Solana
  - **GMGN APIs**: 
    - Price and Charts API
    - Solana Trading API
    - ETH/Base/BSC Trading API
  - **Nitter Integration**: For social signals via NTscraper

### 6. Wallet Integration
- **Phantom Wallet Connection**: 
  - Connect external Phantom wallet
  - Secure authentication flow
  - Transaction signing
- **Internal Wallet System**:
  - Generate wallets for new users
  - Secure key storage
  - Balance management

### 7. Trading Functionality
- **Basic Trading**:
  - Buy/sell operations
  - Coin swaps
  - Price checking
- **Leverage Trading**: Via Mango Client
- **Liquidity Pool Trading**: Through Raydium DEX
- **Auto-Trading**: Risk-based settings and strategies

### 8. UI Interface
- **Login Screen**: Authentication options
- **Main Interface**:
  - "GRACE" title/header
  - Main chat interface
  - Phantom wallet connection button
  - Scrollable side panel for conversation history
  - Settings and withdraw buttons

## Integration Flow

### User Authentication Flow
1. User creates account or logs in
2. System authenticates user credentials
3. One-time disclosure shown (if first login)
4. User session created and linked to memory system

### Conversation Flow
1. User sends message to Grace
2. System processes message through conversation management
3. Topics and entities extracted
4. Relevant memories retrieved
5. If trading intent detected, appropriate API selected
6. Response generated with memory augmentation
7. New information stored in appropriate memory tier

### Trading Flow
1. User expresses trading intent in natural language
2. Grace identifies trading parameters (coin, amount, action)
3. Grace checks wallet balance and market conditions
4. Grace presents confirmation with relevant information
5. Upon confirmation, Grace executes trade through appropriate API
6. Transaction result stored in user's memory

### Memory Update Flow
1. Authorized user sends `!grace.learn` command
2. System verifies user authorization
3. Command parsed to extract entity and update
4. Global memory updated with high priority
5. Confirmation sent to user

## API Integration Details

### Mango Client Integration
- **Purpose**: Leverage trading on Solana
- **Implementation**: Via npm package `@blockworks-foundation/mango-client`
- **Dependencies**: `@solana/web3.js`, `bn.js`
- **Documentation**: https://blockworks-foundation.github.io/mango-client-v3/

### GMGN API Integration
- **Price and Charts API**:
  - **Documentation**: https://docs.gmgn.ai/index/cooperation-api-integrate-gmgn-price-chart
  - **Purpose**: Retrieve crypto price information and charts
  
- **Solana Trading API**:
  - **Documentation**: https://docs.gmgn.ai/index/cooperation-api-integrate-gmgn-solana-trading-api
  - **Purpose**: Execute trades on Solana blockchain
  
- **ETH/Base/BSC Trading API**:
  - **Documentation**: https://docs.gmgn.ai/index/cooperation-api-integrate-gmgn-eth-base-bsc-trading-api
  - **Purpose**: Execute trades on Ethereum, Base, and BSC blockchains

### Nitter Integration
- **Purpose**: Social signals for market sentiment
- **Implementation**: 
  - Connect to Nitter instance (localhost:8085)
  - Use NTscraper for structured data extraction
  - Extract relevant information
  - Associate with entities in memory system
  - Store temporarily in user's personal memory

## Security Considerations

### User Data Security
- Encrypted storage of user profiles
- Secure handling of authentication credentials
- JWT token-based session management

### Wallet Security
- Secure storage of wallet keys
- Transaction signing only with user approval
- No storage of private keys in plaintext

### API Access Security
- Secure handling of API keys
- Rate limiting to prevent abuse
- Error handling for failed API calls

## Environment Configuration
- **FERNET_KEY**: For encryption
- **PHANTOM_APP_URL**: Phantom wallet app URL
- **PHANTOM_CALLBACK_PATH**: Callback path for Phantom wallet
- **PHANTOM_SESSION_PREFIX**: Redis key prefix for Phantom sessions
- **PHANTOM_WALLET_PREFIX**: Redis key prefix for Phantom wallets
- **GMGN_API_URL**: URL for GMGN API

## Future Extensibility
- Modular design allows for adding new APIs
- Memory system can be extended for additional tiers
- Trading functionality can be expanded to new blockchains
- Conversation management can be enhanced with additional features
