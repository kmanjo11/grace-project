"""
Trading Service Selector for Grace

This module provides a non-invasive way to select and manage trading services,
making Mango V3 the primary service while keeping GMGN as a backup.
"""

import logging
from typing import Dict, Any, Optional, Union
from enum import Enum

from src.mango_spot_market import MangoSpotMarket
from src.gmgn_service import GMGNService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        memory_system = None
    ):
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
                conversation_aware=True  # Enable conversation features
            ),
            TradingService.GMGN: GMGNService(
                memory_system=memory_system,
                config=self.config.get("gmgn", {})
            )
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
                "side": "sell" if trade_params.get("side", "buy").lower() == "sell" else "buy",
                "type": trade_params.get("type", "market"),
                "size": float(trade_params["amount"]),
                "user_id": trade_params.get("user_id"),
                "wallet_address": trade_params.get("wallet_address"),
                "client_id": trade_params.get("client_id")
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
                trade_params,
                client_id=trade_params.get('client_id')
            )
            
            if result.get("success", False):
                self.logger.info(f"Trade executed successfully via {self.primary_service.value}")
                return result
                
            # Fallback to GMGN if Mango fails
            self.logger.warning(f"Falling back to GMGN: {result.get('error', 'Unknown error')}")
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
            result = await self.services[self.primary_service].get_user_positions(user_id)
            
            if result.get("success", False):
                return result
                
            return await self.services[TradingService.GMGN].get_wallet_balance(user_id, token)
            
        except Exception as e:
            self.logger.error(f"Error checking balance: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_service(self, service_type: TradingService):
        """Get a specific trading service instance."""
        return self.services.get(service_type)
