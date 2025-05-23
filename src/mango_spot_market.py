"""
Mango Spot Market Integration for Grace

This module provides a direct integration with Mango Markets V3 for spot trading,
designed to work seamlessly with Grace's conversation and agent framework while
maintaining independence for standalone use.

Key features:
- Direct Mango V3 spot trading integration
- Conversation-aware entity mapping
- Background task support
- Compatible with Grace's agent framework
- Can replace GMGN as primary trading service
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from decimal import Decimal

# Grace framework imports (all optional)
try:
    from src.conversation_management import ConversationContext
    from src.agent_framework import AgentTask, TaskPriority

    GRACE_FRAMEWORK_AVAILABLE = True
except ImportError:
    GRACE_FRAMEWORK_AVAILABLE = False

    # Define minimal types for standalone use
    class ConversationContext:
        pass

    class AgentTask:
        pass

    TaskPriority = None

# Mango V3 integration
from src.mango_v3_extension import MangoV3Extension


class EntityMapper:
    """Maps conversation entities to Mango V3 order format."""

    def __init__(self):
        """Initialize the entity mapper with standard trading terms."""
        self.side_mappings = {
            "buy": "buy",
            "purchase": "buy",
            "long": "buy",
            "sell": "sell",
            "short": "sell",
            "exit": "sell",
        }

        self.order_type_mappings = {
            "market": "market",
            "limit": "limit",
            "post_only": "post_only",
            "ioc": "ioc",
            "fill_or_kill": "fill_or_kill",
        }

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("MangoSpotMarket")

    def to_mango_order(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert extracted entities to Mango V3 order format.

        Args:
            entities: Dictionary of extracted entities from conversation

        Returns:
            Dictionary in Mango V3 order format
        """
        order = {
            "market": entities.get("market", "").upper(),
            "side": self.side_mappings.get(entities.get("side", "").lower(), "buy"),
            "type": self.order_type_mappings.get(
                entities.get("type", "").lower(), "market"
            ),
            "size": float(entities.get("size", 0)),
        }

        # Add price for limit orders
        if order["type"] != "market" and "price" in entities:
            order["price"] = float(entities["price"])

        return order


class MangoTaskHandler:
    """Handles background tasks for Mango spot trading."""

    def __init__(self, mango_client: MangoV3Extension):
        """
        Initialize the task handler.

        Args:
            mango_client: Instance of MangoV3Extension
        """
        self.mango = mango_client
        self.logger = logging.getLogger("MangoTaskHandler")

    async def handle_price_check(self, market: str) -> Dict[str, Any]:
        """
        Check current price for a market.

        Args:
            market: Market symbol (e.g. "BTC/USDC")

        Returns:
            Dictionary with price information
        """
        try:
            orderbook = await self.mango.get_orderbook(market)
            return {
                "success": True,
                "market": market,
                "bid": orderbook["bids"][0][0] if orderbook["bids"] else None,
                "ask": orderbook["asks"][0][0] if orderbook["asks"] else None,
                "timestamp": time.time(),
            }
        except Exception as e:
            self.logger.error(f"Price check failed for {market}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def handle_trade_preparation(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a trade by checking requirements.

        Args:
            order: Order parameters

        Returns:
            Dictionary with preparation results
        """
        try:
            # Check market exists
            market_info = await self.mango.get_market(order["market"])
            if not market_info:
                return {"success": False, "error": "Market not found"}

            # Check wallet balance
            balances = await self.mango.get_balances()
            required_balance = order["size"] * (market_info.get("price", 0))

            return {
                "success": True,
                "market": order["market"],
                "sufficient_balance": balances.get(market_info["quote_currency"], 0)
                >= required_balance,
                "required_balance": required_balance,
                "available_balance": balances.get(market_info["quote_currency"], 0),
            }
        except Exception as e:
            self.logger.error(f"Trade preparation failed: {str(e)}")
            return {"success": False, "error": str(e)}


class MangoSpotMarket:
    """
    Main class for Mango Markets spot trading integration.

    This class provides a complete interface for spot trading on Mango Markets,
    with support for Grace's conversation and agent framework while maintaining
    standalone functionality.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        memory_system=None,
        conversation_aware: bool = True,
    ):
        """
        Initialize Mango Spot Market integration.

        Args:
            config: Configuration options
            conversation_aware: Whether to use conversation framework features
        """
        self.config = config or {}
        self.memory_system = memory_system
        self.conversation_aware = conversation_aware and GRACE_FRAMEWORK_AVAILABLE

        # Initialize components
        # Ensure base_url is always defined, falling back to default if not in config
        mango_url = self.config.get("mango_url")
        if mango_url is None:
            mango_url = "http://localhost:8000"
        
        self.logger = logging.getLogger("MangoSpotMarket")
        self.logger.info(f"Initializing MangoV3Extension with base_url={mango_url}")
        
        # Create the MangoV3Extension with the guaranteed non-None base_url
        self.mango = MangoV3Extension(
            base_url=mango_url,
            private_key_path=self.config.get("private_key_path"),
            memory_system=self.memory_system,
        )
        self.entity_mapper = EntityMapper()
        self.task_handler = MangoTaskHandler(self.mango)

        self.logger = logging.getLogger("MangoSpotMarket")

    async def process_trade_request(
        self,
        entities: Dict[str, Any],
        context: Optional[ConversationContext] = None,
        client_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a trade request from either conversation or direct call.

        Args:
            entities: Extracted trading entities
            context: Optional conversation context

        Returns:
            Dictionary with trade result
        """
        try:
            # Convert to Mango order format
            order = self.entity_mapper.to_mango_order(entities)

            # Prepare trade
            prep_result = await self.task_handler.handle_trade_preparation(order)
            if not prep_result["success"]:
                return prep_result

            # Execute trade
            trade_result = await self.mango.place_leverage_trade(
                market=order["market"],
                side=order["side"],
                price=order.get("price", 0),  # 0 for market orders
                size=order["size"],
                leverage=1.0,  # Default to spot (1x)
                reduce_only=False,
                order_type=order["type"],
                client_id=client_id,
            )

            # Store trade in memory system if available
            if self.memory_system:
                trade_memory = {
                    "type": "trade_execution",
                    "source": "mango_v3",
                    "user_id": client_id,
                    "trade_details": order,
                    "result": trade_result,
                    "timestamp": datetime.now().isoformat(),
                }
                self.memory_system.add_to_short_term(
                    user_id=client_id,
                    text=f"Executed {order['side']} trade of {order['size']} {order['market']} via Mango V3",
                    metadata=trade_memory,
                )

            # Update conversation context if available
            if self.conversation_aware and context:
                self._update_context(context, trade_result)

            return trade_result

        except Exception as e:
            self.logger.error(f"Trade request failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _update_context(self, context: ConversationContext, result: Dict[str, Any]):
        """Update conversation context with trade result."""
        if hasattr(context, "add_topic"):
            context.add_topic("trading", 1.0)
            context.add_topic(f"market_{result['market']}", 0.8)

    async def get_market_data(
        self, market_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive market data.

        Args:
            market: Market symbol (e.g. "BTC/USDC")

        Returns:
            Dictionary with market data
        """
        try:
            return await self.mango.get_market_data(market_name)
        except Exception as e:
            self.logger.error(f"Failed to get market data: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_user_positions(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's open positions.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with position information
        """
        try:
            return await self.mango.get_positions(user_id)
        except Exception as e:
            self.logger.error(f"Failed to get positions: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_trade_history(
        self,
        user_identifier: Optional[str] = None,
        trade_type: Optional[str] = "spot",
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Retrieve trade history for spot trades.

        Args:
            user_identifier: Optional user identifier
            trade_type: Optional filter for trade type
            limit: Maximum number of trades to retrieve

        Returns:
            Dictionary of trade history
        """
        try:
            # Use Mango V3 Extension to get trade history
            trades_result = self.mango.get_trade_history(
                user_identifier=user_identifier, trade_type=trade_type, limit=limit
            )

            # Ensure we have a trades list
            trades = trades_result.get("trades", [])

            # Enrich trades with additional metadata
            for trade in trades:
                trade["trade_source"] = "spot_market"

            return {
                "success": True,
                "trades": trades,
                "total_trades": len(trades),
                "metadata": {
                    "user_identifier": user_identifier,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }
        except Exception as e:
            self.logger.error(f"Error retrieving spot trade history: {e}")
            return {"success": False, "error": str(e), "trades": [], "total_trades": 0}

    def place_limit_order(
        self,
        market: str,
        side: str,
        price: float,
        size: float,
        client_id: Optional[str] = None,
        reduce_only: bool = False,
        user_id: Optional[str] = None,  # Optional for tracking
    ) -> Dict[str, Any]:
        """
        Place a limit order for spot trading.

        Args:
            market: Trading market
            side: 'buy' or 'sell'
            price: Limit order price
            size: Order size
            client_id: Optional unique client identifier
            reduce_only: Whether order should only reduce existing position
            user_id: Optional user identifier for tracking

        Returns:
            Limit order placement result
        """
        try:
            # Generate client ID if not provided
            generated_client_id = client_id or f"grace-spot-limit-{int(time.time())}"

            # Place limit order via Mango V3
            order_result = self.mango.place_spot_order(
                market=market,
                side=side,
                price=price,
                size=size,
                order_type="limit",
                client_id=generated_client_id,
                reduce_only=reduce_only,
            )

            # Track limit order
            if order_result.get("success"):
                limit_order_details = {
                    "market": market,
                    "side": side,
                    "price": price,
                    "size": size,
                    "client_id": generated_client_id,
                    "status": "active",
                    "timestamp": time.time(),
                }

                # Optional: Log to memory system
                if self.memory_system and user_id:
                    self.memory_system.create_memory(
                        title=f"Spot Limit Order: {market} {side}",
                        content=json.dumps(limit_order_details),
                        tags=["limit_order", "spot_trade"],
                    )

                self.logger.info(f"Spot limit order placed: {limit_order_details}")
                return {
                    "success": True,
                    "order_details": limit_order_details,
                    **order_result,
                }

            return order_result

        except Exception as e:
            self.logger.error(f"Error placing spot limit order: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


# Example usage
if __name__ == "__main__":

    async def main():
        # Initialize with default config
        mango_spot = MangoSpotMarket()

        # Example trade request
        trade_entities = {
            "market": "BTC/USDC",
            "side": "buy",
            "type": "market",
            "size": 0.1,
        }

        result = await mango_spot.process_trade_request(trade_entities)
        print(f"Trade result: {json.dumps(result, indent=2)}")

    asyncio.run(main())
