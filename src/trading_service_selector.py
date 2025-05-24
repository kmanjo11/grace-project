"""
Trading Service Selector for Grace

This module provides a non-invasive way to select and manage trading services,
making Mango V3 the primary service while keeping GMGN as a backup.
"""

import logging
import time
from typing import Dict, Any, Optional, Union
from enum import Enum

from src.mango_spot_market import MangoSpotMarket
from src.gmgn_service import GMGNService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TradingServiceSelector")


class TradingService(Enum):
    """Available trading services."""

    MANGO = "mango"
    GMGN = "gmgn"


class TradingServiceSelector:
    """
    Manages trading service selection and fallback logic.
    Non-invasive implementation that preserves existing functionality.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, memory_system=None):
        """
        Initialize trading service selector.

        Args:
            config: Configuration options
            memory_system: Memory system for context
        """
        self.config = config or {}
        self.memory_system = memory_system

        # Initialize services with proper configuration
        mango_config = self.config.get("mango", {})
        if not mango_config.get("mango_url"):
            mango_config["mango_url"] = "http://localhost:8000"

        self.services = {
            TradingService.MANGO: MangoSpotMarket(
                config=mango_config,
                conversation_aware=True,  # Enable conversation features
            ),
            TradingService.GMGN: GMGNService(
                memory_system=memory_system, config=self.config.get("gmgn", {})
            ),
        }

        self.primary_service = TradingService.MANGO
        self.logger = logging.getLogger("TradingServiceSelector")

    def _map_trade_params(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map trade parameters between different service formats.

        Args:
            trade_params: Original trade parameters

        Returns:
            Mapped trade parameters
        """
        if "from_token" in trade_params and "to_token" in trade_params:
            # Convert from TradingAgent format to MangoSpot format
            market = f"{trade_params['from_token']}/{trade_params['to_token']}"
            return {
                "market": market,
                "side": (
                    "sell"
                    if trade_params.get("side", "buy").lower() == "sell"
                    else "buy"
                ),
                "type": trade_params.get("type", "market"),
                "size": float(trade_params["amount"]),
                "user_id": trade_params.get("user_id"),
                "wallet_address": trade_params.get("wallet_address"),
                "client_id": trade_params.get("client_id"),
            }
        return trade_params

    async def execute_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade using primary service with fallback.

        Args:
            trade_params: Trade parameters

        Returns:
            Trade result dictionary
        """
        try:
            # Try Mango V3 first
            result = await self.services[self.primary_service].process_trade_request(
                trade_params, client_id=trade_params.get("client_id")
            )

            if result.get("success", False):
                self.logger.info(
                    f"Trade executed successfully via {self.primary_service.value}"
                )
                return result

            # Fallback to GMGN if Mango fails
            self.logger.warning(
                f"Falling back to GMGN: {result.get('error', 'Unknown error')}"
            )
            return await self.services[TradingService.GMGN].execute_trade(trade_params)

        except Exception as e:
            self.logger.error(f"Error in trade execution: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_market_data(self, market: str) -> Dict[str, Any]:
        """
        Get market data using primary service with fallback.

        Args:
            market: Market symbol

        Returns:
            Market data dictionary
        """
        try:
            result = await self.services[self.primary_service].get_market_data(market)

            if result.get("success", False):
                return result

            return await self.services[TradingService.GMGN].get_market_data(market)

        except Exception as e:
            self.logger.error(f"Error getting market data: {str(e)}")
            return {"success": False, "error": str(e)}

    async def check_balance(self, user_id: str, token: str) -> Dict[str, Any]:
        """
        Check balance using primary service with fallback.

        Args:
            user_id: User identifier
            token: Token symbol

        Returns:
            Balance information dictionary
        """
        try:
            result = await self.services[self.primary_service].get_user_positions(
                user_id
            )

            if result.get("success", False):
                return result

            return await self.services[TradingService.GMGN].get_wallet_balance(
                user_id, token
            )

        except Exception as e:
            self.logger.error(f"Error checking balance: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def check_wallet_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Check wallet balance for all tokens using primary service with fallback.
        
        Args:
            user_id: User identifier
            
        Returns:
            Complete wallet balance information for all tokens
        """
        try:
            # Try Mango V3 first for wallet balance
            service = self.services[self.primary_service]
            if hasattr(service, "get_wallet_balance"):
                result = await service.get_wallet_balance(user_id)
                if result.get("success", False):
                    return result
            
            # Then try to get positions which often includes balance info
            positions_result = await service.get_user_positions(user_id)
            if positions_result.get("success", False):
                # Extract balance information from positions
                balances = {}
                for position in positions_result.get("positions", []):
                    token = position.get("symbol", "").split("/")[0] if "/" in position.get("symbol", "") else position.get("symbol", "")
                    if token:
                        balances[token] = {
                            "amount": position.get("size", 0),
                            "value_usd": position.get("notionalValue", 0),
                            "source": "mango_v3"
                        }
                
                return {
                    "success": True,
                    "balances": balances,
                    "platform": "mango_v3"
                }
            
            # Fall back to GMGN service
            self.logger.warning("Falling back to GMGN service for wallet balance")
            return await self.services[TradingService.GMGN].get_wallet_balance(user_id)
            
        except Exception as e:
            self.logger.error(f"Error checking wallet balance: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_service(self, service_type: TradingService):
        """Get a specific trading service instance."""
        return self.services.get(service_type)
        
    async def execute_leverage_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a leverage trade using primary service with fallback.
        
        Args:
            trade_params: Leverage trade parameters
            
        Returns:
            Trade result dictionary
        """
        try:
            # Extract key parameters
            market = trade_params.get("market", "")
            side = trade_params.get("side", "buy")
            size = float(trade_params.get("size", 0))
            leverage = float(trade_params.get("leverage", 1.0))
            price = float(trade_params.get("price", 0))
            order_type = trade_params.get("type", "market")
            reduce_only = trade_params.get("reduce_only", False)
            client_id = trade_params.get("client_id", f"leverage_{int(time.time())}")
            user_id = trade_params.get("user_id")
            
            self.logger.info(
                f"Executing leverage trade: {side} {size} {market} with {leverage}x leverage"
            )
            
            # Try Mango V3 first for leverage trading
            service = self.services[self.primary_service]
            
            # Check if the service has the specific method for leverage trading
            if hasattr(service, "place_leverage_trade"):
                result = await service.place_leverage_trade(
                    market=market,
                    side=side,
                    price=price,
                    size=size,
                    leverage=leverage,
                    order_type=order_type,
                    reduce_only=reduce_only,
                    client_id=client_id
                )
                
                if result.get("success", False):
                    self.logger.info(f"Leverage trade executed successfully via {self.primary_service.value}")
                    return result
                
                error = result.get("error", "Unknown error")
                self.logger.warning(f"Leverage trade failed via {self.primary_service.value}: {error}")
            else:
                self.logger.warning(f"{self.primary_service.value} doesn't support leverage trading directly")
            
            # Fall back to GMGN service for leverage trading
            gmgn_service = self.services[TradingService.GMGN]
            self.logger.info("Falling back to GMGN for leverage trading")
            
            # Adapt parameters for GMGN service format if needed
            gmgn_params = {
                "symbol": market.split("/")[0] if "/" in market else market,
                "action": side,
                "amount": size,
                "leverage": leverage,
                "user_id": user_id
            }
            
            # Call GMGN service for leverage trading
            if hasattr(gmgn_service, "execute_leverage_trade"):
                return await gmgn_service.execute_leverage_trade(**gmgn_params)
            else:
                self.logger.error("No service available for leverage trading")
                return {
                    "success": False,
                    "error": "No service available for leverage trading"
                }
                
        except Exception as e:
            self.logger.error(f"Error in leverage trade execution: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def confirm_trade(self, confirmation_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Confirm a pending trade execution using the primary service with fallback.
        
        Args:
            confirmation_id: The ID of the trade confirmation to process
            user_id: Optional user identifier
            
        Returns:
            Confirmation result dictionary with standardized format
        """
        try:
            # First try using the primary service (Mango V3)
            service = self.services[self.primary_service]
            
            # Check if the service has a confirm_trade method
            if hasattr(service, "confirm_trade"):
                self.logger.info(f"Confirming trade {confirmation_id} via {self.primary_service.value}")
                result = await service.confirm_trade(confirmation_id, user_id)
                
                if result.get("success", False) or result.get("status") == "success":
                    self.logger.info(f"Trade confirmed successfully via {self.primary_service.value}")
                    
                    # Standardize response format
                    if "status" in result and "success" not in result:
                        result["success"] = result["status"] == "success"
                        
                    return result
                    
                error = result.get("error", "Unknown error")
                self.logger.warning(f"Trade confirmation failed via {self.primary_service.value}: {error}")
            
            # Fall back to GMGN service if primary fails
            gmgn_service = self.services[TradingService.GMGN]
            self.logger.info(f"Falling back to GMGN for trade confirmation: {confirmation_id}")
            
            if hasattr(gmgn_service, "confirm_trade"):
                result = await gmgn_service.confirm_trade(confirmation_id, user_id)
                
                # Standardize response format
                if "status" in result and "success" not in result:
                    result["success"] = result["status"] == "success"
                    
                return result
            else:
                self.logger.error("No service available for trade confirmation")
                return {
                    "success": False,
                    "status": "error",
                    "error": "No service available for trade confirmation",
                    "confirmation_id": confirmation_id,
                    "user_id": user_id
                }
                
        except Exception as e:
            self.logger.error(f"Error in trade confirmation: {str(e)}")
            return {
                "success": False,
                "status": "error",
                "error": str(e),
                "code": "CONFIRMATION_ERROR",
                "confirmation_id": confirmation_id,
                "user_id": user_id
            }
            
    async def modify_leverage_position(self, position_id: str, modification_type: str, new_value: Any, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Modify an existing leverage position.
        
        Args:
            position_id: Position identifier
            modification_type: Type of modification (tp, sl, size, leverage)
            new_value: New value for the modification
            user_id: Optional user identifier
            
        Returns:
            Modification result dictionary
        """
        try:
            # Try Mango V3 first
            service = self.services[self.primary_service]
            
            if hasattr(service, "modify_position"):
                result = await service.modify_position(
                    position_id=position_id,
                    modification_type=modification_type,
                    new_value=new_value,
                    user_id=user_id
                )
                
                if result.get("success", False):
                    self.logger.info(f"Position modified successfully via {self.primary_service.value}")
                    return result
                    
                error = result.get("error", "Unknown error")
                self.logger.warning(f"Position modification failed via {self.primary_service.value}: {error}")
                
            # Fall back to GMGN
            gmgn_service = self.services[TradingService.GMGN]
            self.logger.info("Falling back to GMGN for position modification")
            
            if hasattr(gmgn_service, "modify_leverage_position"):
                return await gmgn_service.modify_leverage_position(
                    position_id=position_id,
                    modification_type=modification_type,
                    new_value=new_value,
                    user_id=user_id
                )
            else:
                self.logger.error("No service available for position modification")
                return {
                    "success": False,
                    "error": "No service available for position modification"
                }
                
        except Exception as e:
            self.logger.error(f"Error in position modification: {str(e)}")
            return {"success": False, "error": str(e)}
