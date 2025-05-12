# API Integration Design for Grace

## Overview
This document outlines the API integration design for Grace, focusing on the Nitter, GMGN, and Mango Client services. The design includes verified API calls, integration patterns, and implementation considerations to ensure Grace can effectively interact with these services while maintaining the overall architecture principles.

## API Services

### 1. Nitter Integration
- **Purpose**: Social media data retrieval
- **Implementation**: Integration with ntscraper library (https://github.com/bocchilorenzo/ntscraper)
- **Connection**: Local Nitter instance (localhost:8085)
- **Data Format**: RSS feeds parsed into structured data

#### Verified API Functions
```python
# Core Nitter functions from ntscraper
def get_tweets(term, mode='term', **kwargs):
    """
    Retrieve tweets based on search term or user timeline.
    
    Args:
        term (str): Search term or username
        mode (str): 'term' for search, 'user' for user timeline
        **kwargs: Additional parameters (limit, since, until, etc.)
    
    Returns:
        list: Collection of tweet objects
    """
    pass

def get_tweet_by_id(username, tweet_id):
    """
    Retrieve a specific tweet by its ID.
    
    Args:
        username (str): Username of the tweet author
        tweet_id (str): ID of the tweet to retrieve
    
    Returns:
        dict: Tweet object with details
    """
    pass

def get_profile_info(username, mode='simple'):
    """
    Retrieve profile information for a user.
    
    Args:
        username (str): Username to retrieve info for
        mode (str): 'simple' for basic info, 'extended' for detailed info
    
    Returns:
        dict: User profile information
    """
    pass

def _make_request(endpoint, params):
    """
    Make a request to the Nitter API.
    
    Args:
        endpoint (str): API endpoint to call
        params (dict): Parameters for the request
    
    Returns:
        Response: API response object
    """
    pass
```

#### Integration Pattern
1. Grace receives user request requiring social data
2. NitterService determines appropriate function to call
3. Request made to local Nitter instance
4. RSS data parsed into structured format
5. Data temporarily stored in user's personal memory/context
6. Data associated with relevant Core entities

### 2. GMGN API Integration
- **Purpose**: Coin knowledge, price charts, market analysis, crypto data
- **Base URL**: https://gmgn.ai/defi/router/v1/sol (as specified in .env)
- **Documentation**: 
  - Price Charts: https://docs.gmgn.ai/index/cooperation-api-integrate-gmgn-price-chart
  - Solana Trading: https://docs.gmgn.ai/index/cooperation-api-integrate-gmgn-solana-trading-api
  - ETH/Base/BSC Trading: https://docs.gmgn.ai/index/cooperation-api-integrate-gmgn-eth-base-bsc-trading-api

#### Verified API Functions
```python
# GMGN API functions based on documentation
def get_price_data(token_address, timeframe='1d', limit=100):
    """
    Retrieve price data for a specific token.
    
    Args:
        token_address (str): Address of the token
        timeframe (str): Time interval ('1m', '5m', '15m', '1h', '4h', '1d')
        limit (int): Number of data points to retrieve
    
    Returns:
        dict: Price data including OHLCV
    """
    pass

def get_token_info(token_address):
    """
    Retrieve detailed information about a token.
    
    Args:
        token_address (str): Address of the token
    
    Returns:
        dict: Token information including name, symbol, supply, etc.
    """
    pass

def execute_swap(from_token, to_token, amount, slippage=0.5, wallet_address=None):
    """
    Execute a token swap transaction.
    
    Args:
        from_token (str): Address of token to swap from
        to_token (str): Address of token to swap to
        amount (float): Amount to swap
        slippage (float): Maximum acceptable slippage percentage
        wallet_address (str, optional): Wallet address for the transaction
    
    Returns:
        dict: Transaction details
    """
    pass

def get_market_overview(blockchain='solana'):
    """
    Get overview of market conditions.
    
    Args:
        blockchain (str): Blockchain to get overview for ('solana', 'ethereum', 'base', 'bsc')
    
    Returns:
        dict: Market overview data
    """
    pass
```

#### Integration Pattern
1. Grace identifies need for crypto data or trading operation
2. GMGNService selects appropriate function based on context
3. API call executed with proper parameters
4. Response processed and presented to user
5. Relevant data stored in memory system

### 3. Mango Client Integration
- **Purpose**: Trading operations and crypto data
- **Implementation**: Via npm package `@blockworks-foundation/mango-client`
- **Dependencies**: `@solana/web3.js`, `bn.js`
- **Documentation**: https://blockworks-foundation.github.io/mango-client-v3/

#### Verified API Functions
```python
# Mango Client functions
def open_position(market, side, size, price, position_type='limit'):
    """
    Open a trading position.
    
    Args:
        market (str): Market identifier
        side (str): 'buy' or 'sell'
        size (float): Position size
        price (float): Target price
        position_type (str): 'limit' or 'market'
    
    Returns:
        dict: Order details including order_id
    """
    pass

def close_position(market, order_id):
    """
    Close an existing position.
    
    Args:
        market (str): Market identifier
        order_id (str): ID of the order to close
    
    Returns:
        dict: Closure details
    """
    pass

def set_stop_loss(market, order_id, price):
    """
    Set a stop loss for an existing position.
    
    Args:
        market (str): Market identifier
        order_id (str): ID of the order
        price (float): Stop loss price
    
    Returns:
        dict: Stop loss details
    """
    pass

def get_position(market):
    """
    Get current position details for a market.
    
    Args:
        market (str): Market identifier
    
    Returns:
        dict: Position details
    """
    pass
```

#### Integration Pattern
1. Grace identifies trading intent from user
2. MangoService prepares trading parameters
3. Appropriate trading function called
4. Transaction executed and confirmed
5. Results stored in user's trading history

## Integration with Memory System

### API Data Storage
- **Short-Term Memory**: Current API responses relevant to active conversation
- **Medium-Term Memory**: User-specific API data (trading history, preferences)
- **Long-Term Memory**: General market knowledge and trends

### Bridging with API Services
- **Data Transformation**: Converts API responses to memory-compatible format
- **Entity Linking**: Associates API data with relevant entities
- **Context Integration**: Incorporates API data into conversation context

## Implementation Considerations

### Error Handling
- **Retry Logic**: Implements appropriate retry for transient failures
- **Fallback Mechanisms**: Provides alternative data sources when primary fails
- **User Notification**: Informs user of API issues when relevant

### Rate Limiting
- **Request Throttling**: Prevents exceeding API rate limits
- **Prioritization**: Prioritizes critical requests during high load
- **Caching**: Reduces duplicate requests for the same data

### Security
- **API Key Management**: Securely stores and manages API credentials
- **Request Validation**: Validates all outgoing API requests
- **Response Validation**: Verifies and sanitizes incoming data

## Dynamic API Selection

### Context-Based Routing
- **Intent Recognition**: Identifies which API to use based on user intent
- **Data Requirements**: Determines data needs from conversation context
- **Service Selection**: Chooses appropriate service for each request

### Natural Language Processing
- **Parameter Extraction**: Extracts API parameters from natural language
- **Confirmation**: Confirms critical parameters before execution
- **Response Integration**: Incorporates API responses into natural language

## Integration with Open Interpreter

### Core.py Integration
- **API Manager Registration**: Registers API services with Open Interpreter core
- **Context Sharing**: Shares conversation context with API services
- **Response Handling**: Integrates API responses into interpreter responses

### Command Recognition
- **API Command Patterns**: Recognizes patterns indicating API needs
- **Parameter Mapping**: Maps natural language to API parameters
- **Execution Flow**: Manages flow between conversation and API calls

## Future Extensibility

### New API Integration
- **Standardized Interface**: Common interface for adding new APIs
- **Documentation**: Clear process for integrating additional services
- **Testing Framework**: Validation tools for new integrations

### Enhanced Capabilities
- **Composite Requests**: Combines data from multiple APIs
- **Predictive Fetching**: Anticipates API needs based on context
- **Adaptive Selection**: Learns optimal API selection patterns
