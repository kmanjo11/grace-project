"""
Mango V3 Extension for Grace Trading System

This module provides an optional, non-invasive extension to existing trading capabilities
using Mango V3 as an additional data source and trading option.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class MangoV3Client:
    """
    A lightweight client for the Mango V3 REST API.
    This client is designed to be non-invasive and work alongside existing trading systems.
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost", 
        private_key_path: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Mango V3 client.
        
        Args:
            base_url: URL of the Mango V3 service (default: http://localhost)
            private_key_path: Path to private key file for authenticated requests
            logger: Optional logger for tracking events
        """
        self.base_url = base_url
        self.private_key_path = private_key_path
        self.logger = logger or logging.getLogger(__name__)
        
        # Load private key if provided
        self.private_key = None
        if private_key_path and os.path.exists(private_key_path):
            try:
                with open(private_key_path, 'r') as f:
                    self.private_key = f.read().strip()
                self.logger.info("Loaded private key for Mango V3 client")
            except Exception as e:
                self.logger.error(f"Failed to load private key: {e}")
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Mango V3 API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request body for POST requests
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/api/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            # Light validation of critical responses
            if endpoint.startswith('wallet/'):
                if not isinstance(result, dict):
                    return {"success": False, "error": "Invalid response format"}
                if not result.get('success', False):
                    self.logger.warning(f"Wallet operation failed: {result.get('error', 'Unknown error')}")
            
            return result
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return {"success": False, "error": str(e)}
    
    # GET endpoints
    
    def get_positions(self) -> Dict[str, Any]:
        """Get open positions"""
        return self._make_request("GET", "positions")
    
    def get_coins(self) -> Dict[str, Any]:
        """Get all available coins"""
        return self._make_request("GET", "coins")
    
    def get_wallet_balances(self) -> Dict[str, Any]:
        """
        Get wallet balances with standardized format
        
        Returns:
            Dict with balance information:
            - success: bool
            - balance: float (total balance)
            - details: Dict of individual asset balances
        """
        try:
            result = self._make_request('GET', '/wallet/balances')
            if not result.get('success'):
                return result
                
            balances = result.get('balances', [])
            total_balance = sum(float(bal.get('value', 0)) for bal in balances)
            
            return {
                'success': True,
                'balance': total_balance,
                'details': balances
            }
        except Exception as e:
            self.logger.error(f"Failed to get wallet balances: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_markets(self) -> Dict[str, Any]:
        """Get all markets"""
        return self._make_request("GET", "markets")
    
    def get_market_by_name(self, market_name: str) -> Dict[str, Any]:
        """Get market by name"""
        return self._make_request("GET", f"markets/{market_name}")
    
    def get_orderbook(self, market_name: str) -> Dict[str, Any]:
        """Get orderbook by market name"""
        return self._make_request("GET", f"markets/{market_name}/orderbook")
    
    def get_trades(self, market_name: str) -> Dict[str, Any]:
        """Get trades by market name"""
        return self._make_request("GET", f"markets/{market_name}/trades")
    
    def get_candles(self, market_name: str, resolution: int = 60) -> Dict[str, Any]:
        """
        Get candles/OHLCV by market name
        
        Args:
            market_name: Market name
            resolution: Candle resolution in seconds (default: 60)
            
        Returns:
            Candle data
        """
        return self._make_request("GET", f"markets/{market_name}/candles", params={"resolution": resolution})
    
    def get_order_by_market(self, market_name: str) -> Dict[str, Any]:
        """Get orders by market"""
        return self._make_request("GET", f"orders/{market_name}")

    def get_positions(self, user_identifier: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve user trading positions.
        
        Args:
            user_identifier: Optional user identifier to filter positions
        
        Returns:
            Dict of user positions
        """
        endpoint = f"positions/{user_identifier}" if user_identifier else "positions"
        try:
            positions_data = self._make_request("GET", endpoint)
            
            # Standardize response format
            return {
                "success": True,
                "positions": positions_data.get('positions', []),
                "metadata": {
                    "total_positions": len(positions_data.get('positions', [])),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return {
                "success": False,
                "positions": [],
                "error": {
                    "message": str(e),
                    "code": "POSITION_FETCH_ERROR"
                }
            }

    # POST endpoints
    
    def place_spot_order(
        self, 
        market: str, 
        side: str, 
        price: float, 
        size: float, 
        client_id: Optional[str] = None,
        order_type: str = "limit",
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        Place a spot order
        
        Args:
            market: Market name
            side: Order side (buy or sell)
            price: Order price
            size: Order size
            client_id: Optional client ID
            order_type: Order type (limit, market)
            reduce_only: Whether the order should only reduce position
            
        Returns:
            Order placement result
        """
        data = {
            "market": market,
            "side": side,
            "price": price,
            "size": size,
            "type": order_type,
            "reduceOnly": reduce_only
        }
        
        if client_id:
            data["clientId"] = client_id
            
        return self._make_request("POST", "orders", data=data)
    
    def withdraw_funds(self, coin: str, size: float, address: str) -> Dict[str, Any]:
        """
        Withdraw funds
        
        Args:
            coin: Coin to withdraw
            size: Amount to withdraw
            address: Destination address
            
        Returns:
            Withdrawal result
        """
        data = {
            "coin": coin,
            "size": size,
            "address": address
        }
        
        return self._make_request("POST", "wallet/withdrawals", data=data)
    
    # DELETE endpoints
    
    def cancel_all_orders(self) -> Dict[str, Any]:
        """Cancel all orders"""
        return self._make_request("DELETE", "orders")
    
    def cancel_order_by_client_id(self, client_id: str) -> Dict[str, Any]:
        """Cancel order by client ID"""
        return self._make_request("DELETE", f"orders/by_client_id/{client_id}")
    
    def cancel_order_by_order_id(self, order_id: str) -> Dict[str, Any]:
        """Cancel order by order ID"""
        return self._make_request("DELETE", f"orders/{order_id}")

    def link_wallet(self, wallet_address: str, user_id: str) -> Dict[str, Any]:
        """
        Link a wallet to Mango Markets (simplified, shared access)
        
        Args:
            wallet_address: User's wallet public key
            user_id: Grace application user ID
            
        Returns:
            Linking result
        """
        return self._make_request('POST', 'wallet/link', data={
            'wallet_address': wallet_address,
            'user_id': user_id,
            'link_type': 'shared'
        })
        
    def deposit_funds(self, user_id: str, amount: float, asset: str) -> Dict[str, Any]:
        """
        Deposit funds into Mango Markets
        
        Args:
            user_id: User's unique identifier
            amount: Amount to deposit
            asset: Asset type (e.g., 'USDC')
            
        Returns:
            Deposit result
        """
        return self._make_request('POST', 'wallet/deposit', data={
            'user_id': user_id,
            'amount': str(amount),
            'asset': asset,
            'source': 'internal_wallet'
        })

class MangoV3Extension:
    """
    A lightweight extension to provide Mango V3 trading capabilities
    without modifying existing trade infrastructure.
    """
    
    def __init__(
        self,
        client,
        memory_system=None,
        logger=None,
        transaction_confirmation=None
    ):
        """
        Initialize Mango V3 extension.
        
        Args:
            client: Mango V3 client instance
            memory_system: Optional memory system for storing trade data
            private_key_path: Path to private key file for authenticated requests
            logger: Optional logger
        """
        self.logger = logger or logging.getLogger(__name__)
        self.client = MangoV3Client(base_url, private_key_path, logger)
        self.memory_system = memory_system
        self.transaction_confirmation = transaction_confirmation
        
    def get_market_data(self, market_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get market data from Mango V3.
        
        Args:
            market_name: Optional market name to get specific market data
            
        Returns:
            Market data dictionary
        """
        try:
            if market_name:
                market_data = self.client.get_market_by_name(market_name)
                orderbook = self.client.get_orderbook(market_name)
                
                return {
                    "market": market_data,
                    "orderbook": orderbook
                }
            else:
                return self.client.get_markets()
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return {"error": str(e)}
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get portfolio summary from Mango V3 with standardized margin metrics.
        
        Returns:
            Portfolio summary dictionary with standardized fields:
            - total_equity: Total account value
            - margin_used: Current margin being used
            - free_collateral: Available collateral
            - account_leverage: Current account leverage
            - positions: List of positions with standardized fields
        """
        try:
            balances = self.client.get_wallet_balances()
            positions = self.client.get_positions()
            
            # Calculate standardized metrics
            total_equity = sum(float(bal['value']) for bal in balances)
            margin_used = sum(float(pos.get('margin_used', 0)) for pos in positions)
            free_collateral = total_equity - margin_used
            account_leverage = margin_used / total_equity if total_equity > 0 else 0
            
            # Standardize position data
            standardized_positions = []
            for pos in positions:
                standardized_pos = {
                    'market': pos.get('market'),
                    'side': pos.get('side'),
                    'size': float(pos.get('size', 0)),
                    'entry_price': float(pos.get('entry_price', 0)),
                    'margin_ratio': float(pos.get('margin_ratio', 0)),
                    'liquidation_price': float(pos.get('liquidation_price', 0)),
                    'unrealized_pnl': float(pos.get('unrealized_pnl', 0)),
                    'leverage': float(pos.get('leverage', 1.0))
                }
                standardized_positions.append(standardized_pos)
            
            return {
                'success': True,
                'total_equity': total_equity,
                'margin_used': margin_used,
                'free_collateral': free_collateral,
                'account_leverage': account_leverage,
                'positions': standardized_positions,
                'balances': balances  # Keep original balances for reference
            }
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {"error": str(e)}
    
    def place_leverage_trade(
        self,
        market: str,
        side: str,
        price: float,
        size: float,
        leverage: float = 1.0,
        reduce_only: bool = False,
        order_type: str = 'limit',
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Place a leverage trade on Mango V3.
        
        Args:
            market: Market name
            side: Order side (buy or sell)
            price: Order price
            size: Order size
            leverage: Leverage multiplier (default: 1.0)
            reduce_only: Whether the order should only reduce position
            
        Returns:
            Trade result dictionary
        """
        try:
            # Adjust size based on leverage
            adjusted_size = size * leverage
            
            # Place the order
            result = self.client.place_spot_order(
                market=market,
                side=side,
                price=price,
                size=adjusted_size,
                client_id=client_id or f"grace-{int(time.time())}",
                order_type=order_type,
                reduce_only=reduce_only
            )
            
            # Store trade in memory system if available
            if self.memory_system and client_id:
                try:
                    trade_memory = {
                        'event_type': 'mango_v3_leverage_trade',
                        'market': market,
                        'side': side,
                        'price': price,
                        'size': size,
                        'leverage': leverage,
                        'reduce_only': reduce_only,
                        'order_type': order_type,
                        'timestamp': datetime.utcnow().isoformat(),
                        'trade_result': result  # Include the full trade result for comprehensive tracking
                    }
                    # Store in both short-term and medium-term memory for better retrieval
                    self.memory_system.add_to_short_term(
                        user_id=client_id, 
                        text=f"Executed {side} leverage trade of {size} {market} at {leverage}x via Mango V3", 
                        metadata=trade_memory
                    )
                    self.memory_system.add_to_medium_term(
                        user_id=client_id,
                        text=f"Leverage trade details: {market} {side} {size} at {price}",
                        metadata=trade_memory
                    )
                except Exception as e:
                    self.logger.error(f"Error storing trade in memory: {e}")
            
            return {
                "success": True,
                "order": result,
                "leverage_used": leverage
            }
        except Exception as e:
            self.logger.error(f"Error placing leverage trade: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def link_wallet(self, wallet_address: str, user_id: str) -> Dict[str, Any]:
        """
        Link a wallet to Mango Markets
        
        Args:
            wallet_address: User's wallet public key
            user_id: Grace application user ID
        
        Returns:
            Linking result dictionary
        """
        try:
            # In a real implementation, this would call the Mango Markets API
            # to register the wallet. For now, we'll simulate success.
            
            # Simulate API call to register wallet
            self.logger.info(f"Linking wallet {wallet_address} for user {user_id} to Mango Markets")
            
            # Check if wallet address is valid
            if not wallet_address or len(wallet_address) < 32:
                return {
                    'success': False,
                    'message': 'Invalid wallet address'
                }
            
            # In a real implementation, this would make an API call:
            # result = self.client._make_request(
            #     "POST", 
            #     "wallet/register", 
            #     data={
            #         "wallet_address": wallet_address,
            #         "user_id": user_id
            #     }
            # )
            
            # For now, simulate success
            return {
                'success': True,
                'message': 'Wallet successfully linked to Mango Markets',
                'wallet_address': wallet_address,
                'user_id': user_id
            }
        except Exception as e:
            self.logger.error(f"Error linking wallet to Mango Markets: {e}")
            return {
                'success': False,
                'message': f'Error linking wallet: {str(e)}'
            }

    def get_trade_history(
    self, 
    user_identifier: Optional[str] = None, 
    trade_type: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Retrieve trade history for Mango V3 trades.
    
    Args:
        user_identifier: Optional user identifier
        trade_type: Optional filter for trade type (spot/leverage)
        limit: Maximum number of trades to retrieve
    
    Returns:
        Dictionary of trade history
    """
    try:
        # Validate inputs
        if not user_identifier:
            return {
                "success": False,
                "error": "User identifier is required",
                "trades": [],
                "total_trades": 0
            }
        
        # Initialize trades list
        trades = []
        
        # 1. Attempt to fetch trades directly from Mango API
        try:
            # Use Mango client to fetch trades
            # Assuming self.client is the Mango Markets API client
            mango_trades = self.client.get_user_trades(
                user=user_identifier,
                market_type=trade_type,  # Mango API might use different parameter names
                limit=limit
            )
            
            # Transform Mango API trades to standard format
            for trade in mango_trades:
                trades.append({
                    "market": trade.get('market', ''),
                    "side": trade.get('side', ''),
                    "price": trade.get('price', 0),
                    "size": trade.get('size', 0),
                    "timestamp": trade.get('timestamp', ''),
                    "trade_source": "mango_api",
                    "trade_type": trade.get('type', ''),
                    "trade_id": trade.get('id', ''),
                    "leverage": trade.get('leverage', 1.0)
                })
        except Exception as api_error:
            self.logger.warning(f"Mango API trade fetch failed: {api_error}")
        
        # 2. Fallback to memory system if Mango API fetch fails or returns no trades
        if not trades and self.memory_system:
            try:
                query_params = {
                    "user_id": user_identifier,
                    "memory_types": ["short_term", "medium_term"],
                    "n_results": limit
                }
                
                # Add trade type filter if specified
                if trade_type:
                    query_params["trade_type"] = trade_type
                
                memory_trades = self.memory_system.query_memory(
                    query="trade",
                    **query_params
                )
                
                for memory in memory_trades:
                    trade_details = memory.get('metadata', {})
                    if trade_details.get('event_type') in ['mango_v3_leverage_trade', 'spot_trade']:
                        trade = {
                            "market": trade_details.get('market', ''),
                            "side": trade_details.get('side', ''),
                            "price": trade_details.get('price', 0),
                            "size": trade_details.get('size', 0),
                            "timestamp": memory.get('timestamp', ''),
                            "trade_source": "memory_system",
                            "trade_type": trade_details.get('event_type', ''),
                            "leverage": trade_details.get('leverage', 1.0)
                        }
                        trades.append(trade)
            except Exception as memory_error:
                self.logger.warning(f"Memory system trade fetch failed: {memory_error}")
        
        # Sort trades by timestamp, most recent first
        trades.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        trades = trades[:limit]
        
        return {
            "success": True,
            "trades": trades,
            "total_trades": len(trades),
            "metadata": {
                "user_identifier": user_identifier,
                "timestamp": datetime.utcnow().isoformat(),
                "fetch_sources": ["mango_api", "memory_system"]
            }
        }
    
    except Exception as e:
        self.logger.error(f"Comprehensive error retrieving trade history: {e}")
        return {
            "success": False,
            "error": str(e),
            "trades": [],
            "total_trades": 0
        }

# Example usage
if __name__ == "__main__":
    import time
    
    # Initialize the extension
    mango = MangoV3Extension(base_url="http://localhost")
    
    # Get market data
    markets = mango.get_market_data()
    print(f"Available markets: {len(markets)} markets found")
    
    # Get portfolio summary
    portfolio = mango.get_portfolio_summary()
    print(f"Portfolio: {portfolio}")
    
    # Test wallet linking
    result = mango.link_wallet("5FHwkrdxBc3S4TidqJfhRxzVZrj8xnHKKZwQpWrXKmZa", "test_user")
    print(f"Wallet linking result: {result}")
