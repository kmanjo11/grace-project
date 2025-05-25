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
from datetime import datetime, timedelta


class MangoV3Client:
    """
    A lightweight client for the Mango V3 REST API.
    This client is designed to be non-invasive and work alongside existing trading systems.
    """

    def __init__(
        self,
        base_url: str = "http://localhost",
        private_key_path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
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
                with open(private_key_path, "r") as f:
                    self.private_key = f.read().strip()
                self.logger.info("Loaded private key for Mango V3 client")
            except Exception as e:
                self.logger.error(f"Failed to load private key: {e}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
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
            if endpoint.startswith("wallet/"):
                if not isinstance(result, dict):
                    return {"success": False, "error": "Invalid response format"}
                if not result.get("success", False):
                    self.logger.warning(
                        f"Wallet operation failed: {result.get('error', 'Unknown error')}"
                    )

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
            result = self._make_request("GET", "/wallet/balances")
            if not result.get("success"):
                return result

            balances = result.get("balances", [])
            total_balance = sum(float(bal.get("value", 0)) for bal in balances)

            return {"success": True, "balance": total_balance, "details": balances}
        except Exception as e:
            self.logger.error(f"Failed to get wallet balances: {e}")
            return {"success": False, "message": str(e)}

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
        return self._make_request(
            "GET", f"markets/{market_name}/candles", params={"resolution": resolution}
        )

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
                "positions": positions_data.get("positions", []),
                "metadata": {
                    "total_positions": len(positions_data.get("positions", [])),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return {
                "success": False,
                "positions": [],
                "error": {"message": str(e), "code": "POSITION_FETCH_ERROR"},
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
        reduce_only: bool = False,
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
            "reduceOnly": reduce_only,
        }

        if client_id:
            data["clientId"] = client_id

        return self._make_request("POST", "orders", data=data)

    def confirm_trade(
        self, confirmation_id: str, user_identifier: str = None
    ) -> Dict[str, Any]:
        """
        Confirm and execute a trade based on the confirmation ID.

        Args:
            confirmation_id: Trade confirmation ID (format: trade_action_token_amount_timestamp)
            user_identifier: User identifier

        Returns:
            Dictionary with trade execution result
        """
        try:
            # Parse confirmation ID
            parts = confirmation_id.split("_")
            if len(parts) < 5 or parts[0] != "trade":
                return {
                    "success": False,
                    "error": "Invalid confirmation ID format",
                    "code": "INVALID_CONFIRMATION_ID",
                }

            # Extract trade parameters
            action = parts[1]  # 'buy' or 'sell'
            token = parts[2]  # token symbol
            amount = float(parts[3])  # trade amount

            # Validate parameters
            if action not in ["buy", "sell"]:
                return {
                    "success": False,
                    "status": "error",
                    "error": f"Invalid action: {action}",
                    "code": "INVALID_ACTION",
                    "confirmation_id": confirmation_id,
                }

            # Map to MangoV3 parameters
            side = action  # same format: 'buy' or 'sell'

            # Get proper market name - validate token
            try:
                # Check if token is valid and exists
                if token.upper() in ["SOL", "BTC", "ETH", "BONK", "JTO", "WIF"]:
                    market = f"{token.upper()}/USDC"
                else:
                    # Try to get market info - if available would validate token exists
                    markets = self.get_markets()
                    valid_token = False

                    if isinstance(markets, list):
                        for m in markets:
                            if token.upper() in m.split("/"):
                                market = m
                                valid_token = True
                                break

                    if not valid_token:
                        market = f"{token.upper()}/USDC"  # Default format
            except Exception as e:
                self.logger.warning(
                    f"Market validation failed: {e}, using default format"
                )
                market = f"{token.upper()}/USDC"  # Default format

            # Detect if it's a leverage trade from the confirmation ID
            is_leverage = False
            leverage = 1.0  # Default to spot trade

            # Check for leverage indicator in confirmation ID
            if len(parts) > 5 and parts[5].startswith("lev"):
                is_leverage = True
                try:
                    leverage = float(parts[5].replace("lev", ""))
                except:
                    leverage = 3.0  # Default leverage if parsing fails

            self.logger.info(
                f"Confirming trade: {side} {amount} {token} with ID {confirmation_id}"
            )

            # Execute the trade using place_leverage_trade
            result = self.place_leverage_trade(
                market=market,
                side=side,
                price=0,  # 0 for market orders
                size=amount,
                leverage=leverage,
                reduce_only=False,
                order_type="market",
                client_id=f"confirm_{confirmation_id}",
            )

            # Create a properly structured response that exactly matches GMGN format
            if result.get("success"):
                # Format successful response to match GMGN's expected structure
                return {
                    "success": True,
                    "status": "success",
                    "platform": "mango_v3",
                    "confirmation_id": confirmation_id,
                    "trade_id": result.get("order", {}).get("id")
                    or f"mango_{int(time.time())}",
                    "user_id": user_identifier,
                    "execution_time": datetime.now().isoformat(),
                    "confirmation_details": {
                        "market": market,
                        "side": side,
                        "size": amount,
                        "price": result.get("executed_price")
                        or result.get("order", {}).get("price"),
                        "leverage": leverage,
                        "order_type": "market",
                        "order": result.get("order", {}),
                    },
                }
            else:
                # Format error response to match GMGN's expected structure
                return {
                    "success": False,
                    "status": "error",
                    "platform": "mango_v3",
                    "confirmation_id": confirmation_id,
                    "user_id": user_identifier,
                    "error": result.get("error", "Unknown trade execution error"),
                    "code": result.get("code", "EXECUTION_ERROR"),
                    "execution_time": datetime.now().isoformat(),
                }

            return result

        except Exception as e:
            self.logger.error(f"Trade confirmation failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "status": "error",
                "error": f"Trade confirmation failed: {str(e)}",
                "code": "CONFIRMATION_ERROR",
                "confirmation_id": confirmation_id,
                "user_id": user_identifier,
            }

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
        data = {"coin": coin, "size": size, "address": address}

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
        return self._make_request(
            "POST",
            "wallet/link",
            data={
                "wallet_address": wallet_address,
                "user_id": user_id,
                "link_type": "shared",
            },
        )

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
        return self._make_request(
            "POST",
            "wallet/deposit",
            data={
                "user_id": user_id,
                "amount": str(amount),
                "asset": asset,
                "source": "internal_wallet",
            },
        )


class MangoV3Extension:
    """
    A lightweight extension to provide Mango V3 trading capabilities
    without modifying existing trade infrastructure.
    """

    def __init__(
        self, client=None, memory_system=None, logger=None, transaction_confirmation=None,
        base_url=None, private_key_path=None
    ):
        """
        Initialize Mango V3 extension.

        Args:
            client: Mango V3 client instance
            memory_system: Optional memory system for storing trade data
            logger: Optional logger
            transaction_confirmation: Optional transaction confirmation handler
            base_url: URL of the Mango V3 service (for direct initialization)
            private_key_path: Path to private key file for authenticated requests
        """
        self.logger = logger or logging.getLogger(__name__)
        self.memory_system = memory_system
        self.transaction_confirmation = transaction_confirmation
        
        # Handle two initialization patterns:
        # 1. Directly providing a client instance
        # 2. Providing base_url and private_key_path to create a client instance
        if client is not None:
            self.client = client  # Use the provided client instance
        elif base_url is not None:
            # Create a new MangoV3Client instance
            self.client = MangoV3Client(
                base_url=base_url,
                private_key_path=private_key_path,
                logger=self.logger
            )
            self.logger.info(f"Created new MangoV3Client with base_url: {base_url}")
        else:
            raise ValueError("Either client or base_url must be provided")

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

                return {"market": market_data, "orderbook": orderbook}
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
            total_equity = sum(float(bal["value"]) for bal in balances)
            margin_used = sum(float(pos.get("margin_used", 0)) for pos in positions)
            free_collateral = total_equity - margin_used
            account_leverage = margin_used / total_equity if total_equity > 0 else 0

            # Standardize position data
            standardized_positions = []
            for pos in positions:
                standardized_pos = {
                    "market": pos.get("market"),
                    "side": pos.get("side"),
                    "size": float(pos.get("size", 0)),
                    "entry_price": float(pos.get("entry_price", 0)),
                    "margin_ratio": float(pos.get("margin_ratio", 0)),
                    "liquidation_price": float(pos.get("liquidation_price", 0)),
                    "unrealized_pnl": float(pos.get("unrealized_pnl", 0)),
                    "leverage": float(pos.get("leverage", 1.0)),
                }
                standardized_positions.append(standardized_pos)

            return {
                "success": True,
                "total_equity": total_equity,
                "margin_used": margin_used,
                "free_collateral": free_collateral,
                "account_leverage": account_leverage,
                "positions": standardized_positions,
                "balances": balances,  # Keep original balances for reference
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
        order_type: str = "limit",
        client_id: Optional[str] = None,
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
                reduce_only=reduce_only,
            )

            # Store trade in memory system if available
            if self.memory_system and client_id:
                try:
                    trade_memory = {
                        "event_type": "mango_v3_leverage_trade",
                        "market": market,
                        "side": side,
                        "price": price,
                        "size": size,
                        "leverage": leverage,
                        "reduce_only": reduce_only,
                        "order_type": order_type,
                        "timestamp": datetime.utcnow().isoformat(),
                        "trade_result": result,  # Include the full trade result for comprehensive tracking
                    }
                    # Store in both short-term and medium-term memory for better retrieval
                    self.memory_system.add_to_short_term(
                        user_id=client_id,
                        text=f"Executed {side} leverage trade of {size} {market} at {leverage}x via Mango V3",
                        metadata=trade_memory,
                    )
                    self.memory_system.add_to_medium_term(
                        user_id=client_id,
                        text=f"Leverage trade details: {market} {side} {size} at {price}",
                        metadata=trade_memory,
                    )
                except Exception as e:
                    self.logger.error(f"Error storing trade in memory: {e}")

            return {"success": True, "order": result, "leverage_used": leverage}
        except Exception as e:
            self.logger.error(f"Error placing leverage trade: {e}")
            return {"success": False, "error": str(e)}
            
    def close_position(self, 
                     market_name: str, 
                     position_id: str = None, 
                     size: float = None,
                     price: float = 0,  # 0 for market order
                     user_identifier: str = None) -> Dict[str, Any]:
        """
        Close an existing position according to the Mango v3 documentation.
        
        For a leverage position, this places an order in the opposite direction of the position.
        For a spot position, this sells the held token back to the quote currency.
        
        Args:
            market_name: The market name (e.g., "BTC/USDC")
            position_id: Optional position ID (if not provided, will find by market)
            size: Amount to close (if None, closes entire position)
            price: Limit price (0 for market orders)
            user_identifier: User ID for tracking
        
        Returns:
            Dictionary with position closing result
        """
        try:
            # 1. Get current positions
            positions = self.get_positions(user_identifier)
            
            if not positions.get("success", False):
                return {
                    "success": False, 
                    "error": "Failed to retrieve positions",
                    "status": "error",
                    "code": "POSITIONS_ERROR"
                }
                
            # Get the position data
            position_data = positions.get("positions", [])
            target_position = None
            
            # Find the position to close (by ID or market name)
            for position in position_data:
                if (position_id and position.get("id") == position_id) or \
                   (market_name and position.get("market") == market_name):
                    target_position = position
                    break
                    
            # If no position found, return error
            if not target_position:
                return {
                    "success": False,
                    "error": f"Position not found for market {market_name}",
                    "status": "error",
                    "code": "POSITION_NOT_FOUND"
                }
                
            # 2. Determine parameters for closing order
            position_size = float(target_position.get("size", 0))
            position_side = target_position.get("side", "").lower()
            
            # Determine the opposite side for closing
            close_side = "sell" if position_side == "buy" else "buy"
            
            # Determine size to close
            close_size = abs(size) if size is not None else abs(position_size)
            
            # Validate against position size
            if close_size > abs(position_size):
                return {
                    "success": False,
                    "error": f"Close size {close_size} exceeds position size {abs(position_size)}",
                    "status": "error",
                    "code": "INVALID_CLOSE_SIZE"
                }
                
            # 3. Place order to close position
            order_type = "market" if price == 0 else "limit"
            
            # Generate a unique client ID
            client_id = f"close_{position_id or market_name}_{int(time.time())}"
            
            # Call place_spot_order with reduce_only=True
            result = self.client.place_spot_order(
                market=market_name,
                side=close_side,
                price=price,
                size=close_size,
                client_id=client_id,
                order_type=order_type,
                reduce_only=True  # Important: This ensures the order only reduces position
            )
            
            # 4. Format response
            if result.get("success", False):
                return {
                    "success": True,
                    "status": "success",
                    "message": f"Successfully closed {close_size} of {market_name} position",
                    "market": market_name,
                    "close_side": close_side,
                    "close_size": close_size,
                    "order_type": order_type,
                    "order_id": result.get("id") or client_id,
                    "position_id": position_id,
                    "user_id": user_identifier,
                    "timestamp": datetime.now().isoformat(),
                    "original_position": target_position,
                    "order_details": result
                }
            else:
                return {
                    "success": False,
                    "status": "error",
                    "error": result.get("error", "Unknown error closing position"),
                    "code": result.get("code", "CLOSE_POSITION_ERROR"),
                    "market": market_name,
                    "position_id": position_id,
                    "user_id": user_identifier
                }
                
        except Exception as e:
            self.logger.error(f"Error closing position: {str(e)}", exc_info=True)
            return {
                "success": False,
                "status": "error",
                "error": f"Failed to close position: {str(e)}",
                "code": "CLOSE_POSITION_EXCEPTION",
                "market": market_name,
                "position_id": position_id
            }
            
    def sell_spot_token(self, 
                      token: str, 
                      amount: float,
                      target_token: str = "USDC",
                      price: float = 0,  # 0 for market order
                      user_identifier: str = None) -> Dict[str, Any]:
        """
        Sell a spot token according to the Mango v3 documentation.
        This is a simplified method for selling a specific token back to the target token (usually USDC).
        
        Args:
            token: Token to sell (e.g., "BTC")
            amount: Amount to sell
            target_token: Token to receive (default: "USDC")
            price: Limit price (0 for market orders)
            user_identifier: User ID for tracking
        
        Returns:
            Dictionary with token selling result
        """
        try:
            # 1. Validate token balance
            balances = self.get_wallet_balances()
            
            if not balances.get("success", False):
                return {
                    "success": False,
                    "error": "Failed to retrieve wallet balances",
                    "status": "error",
                    "code": "BALANCES_ERROR"
                }
                
            # Check if user has enough balance
            token_balances = balances.get("details", {})
            token_balance = token_balances.get(token.upper(), 0)
            
            if token_balance < amount:
                return {
                    "success": False,
                    "error": f"Insufficient balance: {token_balance} {token} < {amount} {token}",
                    "status": "error",
                    "code": "INSUFFICIENT_BALANCE"
                }
                
            # 2. Construct market name
            market_name = f"{token.upper()}/{target_token.upper()}"
            
            # 3. Place sell order
            order_type = "market" if price == 0 else "limit"
            
            # Generate a unique client ID
            client_id = f"sell_{token}_{int(time.time())}"
            
            # Call place_spot_order
            result = self.client.place_spot_order(
                market=market_name,
                side="sell",
                price=price,
                size=amount,
                client_id=client_id,
                order_type=order_type,
                reduce_only=False  # Not reducing a position, just selling a token
            )
            
            # 4. Format response
            if result.get("success", False):
                return {
                    "success": True,
                    "status": "success",
                    "message": f"Successfully sold {amount} {token} for {target_token}",
                    "market": market_name,
                    "side": "sell",
                    "size": amount,
                    "order_type": order_type,
                    "order_id": result.get("id") or client_id,
                    "user_id": user_identifier,
                    "timestamp": datetime.now().isoformat(),
                    "order_details": result
                }
            else:
                return {
                    "success": False,
                    "status": "error",
                    "error": result.get("error", "Unknown error selling token"),
                    "code": result.get("code", "SELL_TOKEN_ERROR"),
                    "market": market_name,
                    "token": token,
                    "amount": amount,
                    "user_id": user_identifier
                }
                
        except Exception as e:
            self.logger.error(f"Error selling token: {str(e)}", exc_info=True)
            return {
                "success": False,
                "status": "error",
                "error": f"Failed to sell token: {str(e)}",
                "code": "SELL_TOKEN_EXCEPTION",
                "token": token,
                "amount": amount
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
            self.logger.info(
                f"Linking wallet {wallet_address} for user {user_id} to Mango Markets"
            )

            # Check if wallet address is valid
            if not wallet_address or len(wallet_address) < 32:
                return {"success": False, "message": "Invalid wallet address"}

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
                "success": True,
                "message": "Wallet successfully linked to Mango Markets",
                "wallet_address": wallet_address,
                "user_id": user_id,
            }
        except Exception as e:
            self.logger.error(f"Error linking wallet to Mango Markets: {e}")
            return {"success": False, "message": f"Error linking wallet: {str(e)}"}

    def get_trade_history(
        self,
        user_identifier: Optional[str] = None,
        trade_type: Optional[str] = None,
        limit: int = 50,
        start_time: Optional[Union[int, str]] = None,
        end_time: Optional[Union[int, str]] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve trade history for Mango V3 trades.
        limit: Maximum number of trades to retrieve

        Returns:
            Dictionary of trade history
        """
        try:
            # Parse timestamps if provided
            def parse_time(t):
                if t is None:
                    return None
                if isinstance(t, (int, float)):
                    return datetime.fromtimestamp(t / 1000 if t > 1e12 else t)
                elif isinstance(t, str):
                    try:
                        return datetime.fromisoformat(t.replace("Z", "+00:00"))
                    except ValueError:
                        return None
                return None

            start_dt = parse_time(start_time)
            end_dt = parse_time(end_time) or datetime.utcnow()

            # Apply cursor if provided
            since_id = None
            if cursor:
                try:
                    cursor_data = json.loads(base64.b64decode(cursor).decode("utf-8"))
                    since_id = cursor_data.get("since_id")
                    if "before_timestamp" in cursor_data:
                        end_dt = parse_time(cursor_data["before_timestamp"])
                except (json.JSONDecodeError, binascii.Error):
                    pass

            trades = []
            next_cursor = None
            has_more = False

            # Get trades from Mango V3 API
            try:
                mango_trades = self.client.get_trades()
                if mango_trades and "trades" in mango_trades:
                    for trade in mango_trades["trades"]:
                        if user_identifier and trade.get("user_id") != user_identifier:
                            continue
                        if trade_type and trade.get("type") != trade_type:
                            continue

                        trade_timestamp = parse_time(trade.get("timestamp"))
                        if not trade_timestamp:
                            continue

                        # Apply time filters
                        if start_dt and trade_timestamp < start_dt:
                            continue
                        if end_dt and trade_timestamp > end_dt:
                            has_more = True
                            continue

                        trades.append(
                            {
                                "id": trade.get("id", str(uuid.uuid4())),
                                "market": trade.get("market", ""),
                                "side": trade.get("side", ""),
                                "price": float(trade.get("price", 0)),
                                "size": float(trade.get("size", 0)),
                                "timestamp": trade_timestamp.isoformat(),
                                "trade_source": "mango_api",
                                "trade_type": trade.get("type", "spot"),
                                "leverage": float(trade.get("leverage", 1.0)),
                            }
                        )
            except Exception as api_error:
                self.logger.warning(f"Mango V3 API trade fetch failed: {api_error}")

            # Get trades from memory system if available
            if self.memory_system:
                try:
                    query_params = {
                        "user_id": user_identifier,
                        "limit": limit,
                        "start_time": start_dt.isoformat() if start_dt else None,
                        "end_time": end_dt.isoformat() if end_dt else None,
                    }
                    if trade_type:
                        query_params["event_type"] = trade_type
                    if since_id:
                        query_params["since_id"] = since_id

                    memory_trades = self.memory_system.query_memory(
                        query="trade",
                        **{k: v for k, v in query_params.items() if v is not None},
                    )

                    for memory in memory_trades:
                        trade_details = memory.get("metadata", {})
                        if trade_details.get("event_type") in [
                            "mango_v3_leverage_trade",
                            "spot_trade",
                        ]:
                            trade_timestamp = parse_time(memory.get("timestamp"))
                            if not trade_timestamp:
                                continue

                            trades.append(
                                {
                                    "id": memory.get("id", str(uuid.uuid4())),
                                    "market": trade_details.get("market", ""),
                                    "side": trade_details.get("side", ""),
                                    "price": float(trade_details.get("price", 0)),
                                    "size": float(trade_details.get("size", 0)),
                                    "timestamp": trade_timestamp.isoformat(),
                                    "trade_source": "memory_system",
                                    "trade_type": trade_details.get("event_type", ""),
                                    "leverage": float(
                                        trade_details.get("leverage", 1.0)
                                    ),
                                }
                            )
                except Exception as memory_error:
                    self.logger.warning(
                        f"Memory system trade fetch failed: {memory_error}"
                    )

            # Sort trades by timestamp, most recent first
            trades.sort(
                key=lambda x: (x.get("timestamp", ""), x.get("id", "")), reverse=True
            )

            # Apply limit and prepare next cursor
            if len(trades) > limit:
                has_more = True
                trades = trades[:limit]

                if trades:
                    last_trade = trades[-1]
                    next_cursor = base64.b64encode(
                        json.dumps(
                            {
                                "since_id": last_trade["id"],
                                "before_timestamp": last_trade["timestamp"],
                            }
                        ).encode("utf-8")
                    ).decode("utf-8")

            return {
                "success": True,
                "trades": trades,
                "pagination": {
                    "has_more": has_more,
                    "next_cursor": next_cursor,
                    "limit": limit,
                    "total": len(trades),
                },
                "metadata": {
                    "user_identifier": user_identifier,
                    "start_time": start_dt.isoformat() if start_dt else None,
                    "end_time": end_dt.isoformat() if end_dt else None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "fetch_sources": ["mango_api", "memory_system"],
                },
            }
        except Exception as e:
            self.logger.error(f"Comprehensive error retrieving trade history: {e}")
            return {
                "success": False,
                "error": str(e),
                "trades": [],
                "pagination": {
                    "has_more": False,
                    "next_cursor": None,
                    "limit": limit,
                    "total": 0,
                },
                "metadata": {
                    "user_identifier": user_identifier,
                    "start_time": start_dt.isoformat() if start_dt else None,
                    "end_time": end_dt.isoformat() if end_dt else None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "fetch_sources": ["mango_api", "memory_system"],
                },
            }

    def _create_error_response(
        self,
        error_message: str,
        error_code: str = None,
        status_code: int = 400,
        **additional_info,
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.

        Args:
            error_message: Human-readable error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            additional_info: Any additional error context

        Returns:
            Dictionary with error information
        """
        error_data = {
            "success": False,
            "error": {
                "message": error_message,
                "code": error_code or "api_error",
                "status": status_code,
                "timestamp": datetime.utcnow().isoformat(),
                **additional_info,
            },
            "position_history": [],
            "pagination": {
                "has_more": False,
                "limit": additional_info.get("limit", 100),
                "total": 0,
            },
            "metadata": {
                "user_identifier": additional_info.get("user_identifier", ""),
                "market": additional_info.get("market", "all"),
                "start_time": additional_info.get("start_time"),
                "end_time": additional_info.get("end_time"),
                "interval": additional_info.get("interval", "1d"),
                "total_positions": 0,
                "has_more": False,
            },
        }
        return error_data

    def _validate_position_history_params(
        self, params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate position history parameters.

        Args:
            params: Dictionary of parameters to validate

        Returns:
            Error response if validation fails, None otherwise
        """
        if not params.get("user_identifier"):
            return self._create_error_response(
                "User identifier is required", "missing_parameter", 400, **params
            )

        try:
            # Validate limit range
            limit = params.get("limit", 100)
            if not (1 <= limit <= 1000):
                return self._create_error_response(
                    "Limit must be between 1 and 1000",
                    "invalid_parameter",
                    400,
                    **params,
                )

            # Validate interval format
            interval = params.get("interval", "1d")
            if not re.match(r"^\d+[mhdw]$", interval):
                return self._create_error_response(
                    "Invalid interval format. Use format like 1m, 1h, 1d, 1w",
                    "invalid_parameter",
                    400,
                    **params,
                )

        except Exception as e:
            return self._create_error_response(
                f"Invalid parameters: {str(e)}", "invalid_parameters", 400, **params
            )

        return None

    def get_position_history(
        self,
        user_identifier: str,
        market: Optional[str] = None,
        start_time: Optional[Union[int, str]] = None,
        end_time: Optional[Union[int, str]] = None,
        interval: str = "1d",
        include_pnl: bool = True,
        cursor: Optional[str] = None,
        limit: int = 100,
        include_live_pnl: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieve historical position data with P&L calculation over time.

        Args:
            user_identifier: Unique identifier for the user
            market: Optional market filter (e.g., 'BTC-PERP')
            start_time: Start time as timestamp (seconds or ms) or ISO format string
            end_time: End time as timestamp (seconds or ms) or ISO format string
            interval: Time interval for position snapshots ('1m', '1h', '1d', etc.)
            include_pnl: Whether to include P&L calculations
            cursor: Pagination cursor for fetching next page of results
            limit: Maximum number of position snapshots to return (default: 100, max: 1000)
            include_live_pnl: Whether to include live P&L calculations for open positions

        Returns:
            Dictionary containing position history with timestamps and P&L data
        """
        try:
            # Prepare params for validation and error context
            params = {
                "user_identifier": user_identifier,
                "market": market,
                "start_time": start_time,
                "end_time": end_time,
                "interval": interval,
                "limit": limit,
                "cursor": cursor,
            }

            # Validate parameters
            validation_error = self._validate_position_history_params(params)
            if validation_error:
                return validation_error

            # Convert string timestamps to datetime objects
            def parse_time(t):
                if t is None:
                    return None
                if isinstance(t, (int, float)):
                    # Handle both seconds and milliseconds
                    if t > 1e12:  # Likely milliseconds
                        return datetime.fromtimestamp(t / 1000)
                    return datetime.fromtimestamp(t)
                elif isinstance(t, str):
                    try:
                        return datetime.fromisoformat(t.replace("Z", "+00:00"))
                    except ValueError:
                        return datetime.utcnow()
                return datetime.utcnow()

            now = datetime.utcnow()
            end_dt = parse_time(end_time) if end_time else now
            start_dt = (
                parse_time(start_time) if start_time else (end_dt - timedelta(days=30))
            )

            # Parse cursor for pagination
            cursor_data = {}
            if cursor:
                try:
                    import base64
                    import json

                    cursor_data = json.loads(base64.b64decode(cursor).decode("utf-8"))
                    # Update start_time from cursor if not explicitly provided
                    if "last_timestamp" in cursor_data and not start_time:
                        start_dt = parse_time(cursor_data["last_timestamp"])
                except Exception as e:
                    self.logger.warning(f"Invalid cursor provided: {e}")

            # Get trades for the user with pagination
            trade_limit = min(
                1000, max(limit * 2, 100)
            )  # Get more trades than needed for better pagination
            trade_history = self.get_trade_history(
                user_identifier=user_identifier, limit=trade_limit, cursor=cursor
            )

            if not trade_history.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to fetch trade history: {trade_history.get('error', 'Unknown error')}",
                    "position_history": [],
                    "pagination": {"has_more": False, "limit": limit, "total": 0},
                    "metadata": {
                        "user_identifier": user_identifier,
                        "market": market or "all",
                        "start_time": start_dt.isoformat() if start_dt else None,
                        "end_time": end_dt.isoformat() if end_dt else None,
                        "interval": interval,
                        "total_positions": 0,
                        "has_more": False,
                    },
                }

            # Process trades into position history
            position_history = []
            current_positions = {}

            # Sort trades by timestamp
            trades = sorted(
                trade_history.get("trades", []), key=lambda x: x.get("timestamp", "")
            )

            # Track if there are more trades available
            has_more_trades = trade_history.get("pagination", {}).get("has_more", False)
            total_trades = trade_history.get("pagination", {}).get("total", 0)

            # Process each trade and track positions over time
            for trade in trades:
                trade_time = parse_time(trade.get("timestamp"))
                if not trade_time or trade_time < start_dt or trade_time > end_dt:
                    continue

                market_name = trade.get("market")
                if market and market_name != market:
                    continue

                # Initialize position if it doesn't exist
                if market_name not in current_positions:
                    current_positions[market_name] = {
                        "market": market_name,
                        "size": 0,
                        "entry_price": 0,
                        "leverage": float(trade.get("leverage", 1.0)),
                        "side": trade.get("side", "buy"),
                        "pnl": 0,
                        "unrealized_pnl": 0,
                        "realized_pnl": 0,
                        "timestamp": trade_time.isoformat(),
                        "trades": [],
                    }

                # Update position based on trade
                position = current_positions[market_name]
                trade_size = float(trade.get("size", 0))
                trade_price = float(trade.get("price", 0))

                # Calculate position changes
                if trade.get("side") == "buy":
                    # Update position size and average entry price
                    total_size = position["size"] + trade_size
                    if total_size != 0:
                        position["entry_price"] = (
                            (position["entry_price"] * position["size"])
                            + (trade_price * trade_size)
                        ) / total_size
                    position["size"] = total_size
                else:  # sell
                    # Calculate P&L for the closed portion
                    if position["size"] > 0:
                        pnl = (trade_price - position["entry_price"]) * min(
                            trade_size, position["size"]
                        )
                        position["realized_pnl"] += pnl
                        position["pnl"] += pnl
                        position["size"] = max(0, position["size"] - trade_size)

                # Add trade to position history
                position["trades"].append(
                    {
                        "timestamp": trade.get("timestamp"),
                        "side": trade.get("side"),
                        "price": trade_price,
                        "size": trade_size,
                        "leverage": float(trade.get("leverage", 1.0)),
                    }
                )

                # Update position timestamp
                position["timestamp"] = trade_time.isoformat()

                # Add position snapshot to history
                position_history.append(
                    {
                        "market": market_name,
                        "size": position["size"],
                        "entry_price": position["entry_price"],
                        "leverage": position["leverage"],
                        "side": position["side"],
                        "pnl": position["pnl"],
                        "realized_pnl": position["realized_pnl"],
                        "unrealized_pnl": position["unrealized_pnl"],
                        "timestamp": position["timestamp"],
                    }
                )

            # If no trades but we have current positions, include them
            if not position_history and current_positions:
                for market_name, position in current_positions.items():
                    if market and market_name != market:
                        continue
                    position_history.append(
                        {
                            "market": market_name,
                            "size": position["size"],
                            "entry_price": position["entry_price"],
                            "leverage": position["leverage"],
                            "side": position["side"],
                            "pnl": position["pnl"],
                            "realized_pnl": position["realized_pnl"],
                            "unrealized_pnl": position["unrealized_pnl"],
                            "timestamp": position["timestamp"],
                        }
                    )

            # Sort position history by timestamp (newest first)
            position_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            # Apply limit for pagination
            has_more = len(position_history) > limit
            paginated_history = position_history[:limit]

            # Calculate P&L over time if requested
            pnl_over_time = []
            if include_pnl and paginated_history:
                # Group positions by timestamp and calculate total P&L
                pnl_dict = {}
                for pos in paginated_history:
                    timestamp = pos["timestamp"]
                    if timestamp not in pnl_dict:
                        pnl_dict[timestamp] = {
                            "timestamp": timestamp,
                            "total_pnl": 0,
                            "markets": {},
                        }

                    # Update market-specific P&L
                    market_name = pos["market"]
                    pnl_dict[timestamp]["markets"][market_name] = {
                        "size": pos["size"],
                        "entry_price": pos["entry_price"],
                        "pnl": pos["pnl"],
                        "realized_pnl": pos["realized_pnl"],
                        "unrealized_pnl": pos["unrealized_pnl"],
                    }

                    # Update total P&L
                    pnl_dict[timestamp]["total_pnl"] += pos["pnl"]

                # Convert to list and sort by timestamp (oldest first)
                pnl_over_time = sorted(pnl_dict.values(), key=lambda x: x["timestamp"])

            # Generate next cursor if there are more results
            next_cursor = None
            if has_more and paginated_history:
                last_timestamp = paginated_history[-1].get("timestamp")
                if last_timestamp:
                    cursor_data = {
                        "last_timestamp": last_timestamp,
                        "offset": len(paginated_history),
                    }
                    try:
                        import base64
                        import json

                        next_cursor = base64.b64encode(
                            json.dumps(cursor_data).encode("utf-8")
                        ).decode("utf-8")
                    except Exception as e:
                        self.logger.warning(f"Failed to generate next cursor: {e}")

            # Include live P&L for open positions if requested
            if include_live_pnl:
                current_markets = {
                    pos["market"]
                    for pos in paginated_history
                    if pos.get("size", 0) != 0
                }
                if current_markets:
                    try:
                        # Get current market prices
                        market_prices = {}
                        for mkt in current_markets:
                            market_data = self.get_market_data(mkt)
                            if market_data and "last_price" in market_data:
                                market_prices[mkt] = float(market_data["last_price"])

                        # Update unrealized P&L for open positions
                        for pos in paginated_history:
                            if pos["size"] != 0 and pos["market"] in market_prices:
                                current_price = market_prices[pos["market"]]
                                pos["unrealized_pnl"] = (
                                    current_price - pos["entry_price"]
                                ) * pos["size"]
                                pos["pnl"] = pos["realized_pnl"] + pos["unrealized_pnl"]
                    except Exception as e:
                        self.logger.error(f"Error calculating live P&L: {e}")

            # Prepare response
            response = {
                "success": True,
                "position_history": paginated_history,
                "pnl_over_time": pnl_over_time if include_pnl else [],
                "pagination": {
                    "has_more": has_more,
                    "next_cursor": next_cursor,
                    "limit": limit,
                    "total": len(paginated_history),
                },
                "metadata": {
                    "user_identifier": user_identifier,
                    "market": market or "all",
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                    "interval": interval,
                    "total_positions": len(paginated_history),
                    "has_more": has_more,
                },
            }

            return response

        except Exception as e:
            self.logger.error(
                f"Error retrieving position history: {str(e)}", exc_info=True
            )
            return self._create_error_response(
                f"Internal server error: {str(e)}",
                "internal_server_error",
                500,
                **params,
                exception_type=e.__class__.__name__,
                traceback=traceback.format_exc(),
            )

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
        result = mango.link_wallet(
            "5FHwkrdxBc3S4TidqJfhRxzVZrj8xnHKKZwQpWrXKmZa", "test_user"
        )
        print(f"Wallet linking result: {result}")
