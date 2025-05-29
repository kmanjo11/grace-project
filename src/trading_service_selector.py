"""
Trading Service Selector for Grace

This module provides a non-invasive way to select and manage trading services,
making Mango V3 the primary service while keeping GMGN as a backup.
"""

import logging
import time
from typing import Dict, Any, Optional
from enum import Enum

# Local imports
try:
    from .mango_spot_market import MangoSpotMarket
except ImportError:
    from mango_spot_market import MangoSpotMarket

try:
    from .gmgn_service import GMGNService
except ImportError:
    from gmgn_service import GMGNService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
_LOGGER = logging.getLogger("TradingServiceSelector")


class TradingService(Enum):
    """Available trading services."""

    MANGO = "mango"
    GMGN = "gmgn"


class TradingServiceSelector:
    """
    Manages trading service selection and fallback logic.
    Non-invasive implementation that preserves existing functionality.
    
    Trading Execution Flow:
    ========================
    1. Frontend (React/TypeScript):
       - User initiates trade via UI components (Trading.tsx, OrderForm.tsx)
       - Trade parameters are validated and formatted
       - API call to /api/trade/execute endpoint
    
    2. API Layer (FastAPI):
       - Validates JWT and permissions
       - Forwards request to TradingServiceSelector
    
    3. TradingServiceSelector (this class):
       - Receives trade parameters
       - Maps parameters to service-specific format
       - Selects primary service (Mango V3 by default)
       - Handles fallback to secondary services (GMGN) if primary fails
    
    4. Service Layer (MangoSpotMarket/GMGNService):
       - MangoSpotMarket for spot trading:
         * Uses MangoV3Extension for direct market access
         * Handles order routing and execution
         * Manages order state and confirmation
       - GMGNService as fallback:
         * Provides backup trading functionality
         * Handles different market conditions
    
    5. Order Execution:
       - Spot Trades:
         * Market/limit orders via place_spot_order
         * Direct execution on Mango V3 orderbook
       - Leverage Trades:
         * Handled by MangoV3Extension.place_leverage_trade
         * Manages margin and position sizing
       - Smart Routing:
         * Splits large orders across multiple venues
         * Implements TWAP/VWAP strategies
    
    Error Handling & Recovery:
    ---------------------------
    - Automatic retries on transient failures
    - Fallback to secondary services
    - Circuit breakers for excessive failures
    - Comprehensive logging and monitoring
    
    Known Limitations:
    ------------------
    - Limited smart order routing capabilities
    - Basic price impact protection needed
    - Could benefit from more sophisticated execution algorithms
    - Consider adding more robust error recovery mechanisms
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, memory_system=None, logger=None):
        """
        Initialize trading service selector.

        Args:
            config: Configuration options
            memory_system: Memory system for context
            logger: Optional logger instance
        """
        self.config = config or {}
        self.memory_system = memory_system
        self.logger = logger or _LOGGER
        
        # Configure logger with proper handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            self.logger.propagate = False

        # Initialize services with proper configuration
        mango_config = self.config.get("mango", {})
        if not mango_config.get("mango_url"):
            mango_config["mango_url"] = "http://mango-v3-service:8080"
            
        # Ensure proper logger is passed to services    
        mango_config["logger"] = self.logger
        gmgn_config = self.config.get("gmgn", {})
        gmgn_config["logger"] = self.logger
        
        # Initialize services
        try:
            self.services = {
                TradingService.MANGO: MangoSpotMarket(
                    config=mango_config,
                    memory_system=memory_system,
                    conversation_aware=True
                ),
                TradingService.GMGN: GMGNService(
                    config=gmgn_config,
                    memory_system=memory_system
                ),
            }
            self.primary_service = TradingService.MANGO
            self.logger.info(
                "Trading services initialized with primary: %s",
                self.primary_service.value
            )
        except Exception as e:
            self.logger.exception(
                "Failed to initialize trading services: %s",
                str(e)
            )
            raise RuntimeError("Failed to initialize trading services") from e

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
            Dict containing:
                - success (bool): Whether the operation was successful
                - error (str, optional): Error message if operation failed
                - code (str, optional): Error code if operation failed
        """
        try:
            # Map trade parameters to service format
            mapped_params = self._map_trade_params(trade_params)
            
            # Try primary service first
            service = self.services[self.primary_service]
            result = await service.execute_trade(mapped_params)
            
            if result.get("success", False):
                self.logger.info(
                    "Trade executed successfully via %s",
                    self.primary_service.value
                )
                return result
                
            error = result.get("error", "Unknown error")
            self.logger.warning(
                "Trade execution failed via %s: %s",
                self.primary_service.value, error
            )
            
            # Fall back to GMGN
            gmgn_service = self.services[TradingService.GMGN]
            self.logger.info("Falling back to GMGN for trade execution")
            
            # Map parameters for GMGN if needed
            gmgn_params = self._map_trade_params(trade_params)
            gmgn_result = await gmgn_service.execute_trade(gmgn_params)
            
            if gmgn_result.get("success", False):
                self.logger.info("Trade executed successfully via GMGN")
            return gmgn_result
            
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid trade parameters: {str(e)}"
            return {
                "success": False,
                "error": error_msg % str(e),
                "code": "INVALID_PARAMETERS"
            }
        except (ConnectionError, TimeoutError) as e:
            error_msg = "Connection error executing trade: %s"
            self.logger.error(error_msg, str(e))
            return {
                "success": False,
                "error": error_msg % str(e),
                "code": "TRADE_CONNECTION_ERROR"
            }
        except Exception as e:  # pylint: disable=broad-except
            error_msg = "Error executing trade: %s"
            self.logger.exception(error_msg, str(e))
            return {
                "success": False,
                "error": error_msg,
                "code": "TRADE_EXECUTION_ERROR"
            }

    async def get_market_data(self, market: str) -> Dict[str, Any]:
        """
        Get market data using primary service with fallback.

        Args:
            market: Market symbol to fetch data for

        Returns:
            Dict containing:
                - success (bool): Whether the operation was successful
                - data (dict, optional): Market data if successful
                - error (str, optional): Error message if operation failed
                - code (str, optional): Error code if operation failed
        """
        try:
            # Try primary service first
            service = self.services[self.primary_service]
            result = await service.get_market_data(market)
            
            if result.get("success", False):
                self.logger.debug(
                    "Market data for %s fetched successfully via %s",
                    market, self.primary_service.value
                )
                return result
                
            error = result.get("error", "Unknown error")
            self.logger.warning(
                "Market data fetch failed for %s via %s: %s",
                market, self.primary_service.value, error
            )
            
            # Fall back to GMGN
            gmgn_service = self.services[TradingService.GMGN]
            self.logger.info(
                "Falling back to GMGN for market data: %s",
                market
            )
            
            gmgn_result = await gmgn_service.get_market_data(market)
            if gmgn_result.get("success", False):
                self.logger.debug(
                    "Market data for %s fetched successfully via GMGN",
                    market
                )
            return gmgn_result
            
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid market symbol {market}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "INVALID_MARKET"
            }
        except (ConnectionError, TimeoutError) as e:
            error_msg = "Failed to connect to market data service: %s"
            self.logger.error(error_msg, str(e))
            return {
                "success": False,
                "error": error_msg % str(e),
                "code": "MARKET_DATA_CONNECTION_ERROR"
            }
        except (RuntimeError, ValueError, KeyError) as e:
            error_msg = f"Failed to process market data for {market}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "MARKET_DATA_PROCESSING_ERROR"
            }
        except Exception as e:  # pylint: disable=broad-except
            error_msg = f"Unexpected error fetching market data for {market}: {str(e)}"
            self.logger.exception(error_msg)
            return {
                "success": False,
                "error": "An unexpected error occurred while fetching market data",
                "code": "MARKET_DATA_ERROR",
                "details": str(e)
            }

    async def _get_balance_from_primary_service(
        self,
        service: Any,
        user_id: str,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """Get token balance from primary service if available.
        
        Args:
            service: The trading service to use
            user_id: User identifier (last 4 chars shown in logs)
            token: Token symbol to check
            
        Returns:
            Dict with balance if successful, None otherwise
        """
        if not hasattr(service, "get_token_balance"):
            self.logger.debug(
                "%s service doesn't support direct balance check",
                self.primary_service.value
            )
            return None
            
        try:
            result = await service.get_token_balance(user_id, token)
            if result.get("success", False):
                self.logger.debug(
                    "[%s] Balance check successful for %s (user: %s)",
                    self.primary_service.value, token, user_id[-4:]
                )
                return result
                
            self.logger.warning(
                "[%s] Balance check failed for %s (user: %s): %s",
                self.primary_service.value, token, user_id[-4:],
                result.get("error", "Unknown error")
            )
            return None
            
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error(
                "[%s] Balance check error for %s (user: %s): %s",
                self.primary_service.value, token, user_id[-4:],
                str(e), exc_info=True
            )
            return None

    async def _get_balance_from_positions(
        self,
        service: Any,
        user_id: str,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """Get token balance from user positions.
        
        Args:
            service: The trading service to use
            user_id: User identifier (last 4 chars shown in logs)
            token: Token symbol to check
            
        Returns:
            Dict with position data if found, None otherwise
        """
        try:
            self.logger.debug(
                "[%s] Checking positions for %s (user: %s)",
                self.primary_service.value, token, user_id[-4:]
            )
            
            positions = await service.get_user_positions(user_id)
            if not positions.get("success", False):
                self.logger.debug(
                    "[%s] No positions found for user: %s",
                    self.primary_service.value, user_id[-4:]
                )
                return None
                
            for position in positions.get("positions", []):
                if position.get("symbol", "").startswith(f"{token}/"):
                    balance = position.get("size", 0)
                    self.logger.debug(
                        "[%s] Found position for %s: %s (user: %s)",
                        self.primary_service.value, token, balance, user_id[-4:]
                    )
                    return {
                        "success": True,
                        "balance": balance,
                        "token": token,
                        "source": self.primary_service.value
                    }
                    
            self.logger.debug(
                "[%s] No %s positions found for user: %s",
                self.primary_service.value, token, user_id[-4:]
            )
            return None
            
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error(
                "[%s] Failed to get positions (user: %s): %s",
                self.primary_service.value, user_id[-4:], str(e),
                exc_info=True
            )
            return None

    async def _get_balance_from_gmgn(
        self,
        user_id: str,
        token: str
    ) -> Dict[str, Any]:
        """Get token balance from GMGN fallback service.
        
        Args:
            user_id: User identifier (last 4 chars shown in logs)
            token: Token symbol to check
            
        Returns:
            Dict with balance information from GMGN service
        """
        self.logger.debug(
            "[GMGN] Falling back to GMGN for %s balance (user: %s)",
            token, user_id[-4:]
        )
        
        try:
            gmgn_service = self.services[TradingService.GMGN]
            result = await gmgn_service.get_wallet_balance(user_id, token)
            
            if result.get("success", False):
                self.logger.debug(
                    "[GMGN] Balance for %s: %s (user: %s)",
                    token, result.get("balance", 0), user_id[-4:]
                )
            else:
                self.logger.warning(
                    "[GMGN] Failed to get balance for %s (user: %s): %s",
                    token, user_id[-4:], result.get("error", "Unknown error")
                )
                
            return result
            
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error(
                "[GMGN] Error getting balance for %s (user: %s): %s",
                token, user_id[-4:], str(e),
                exc_info=True
            )
            return {
                "success": False,
                "error": "Failed to get balance from GMGN",
                "code": "GMGN_BALANCE_ERROR"
            }

    async def check_balance(
        self,
        user_id: str,
        token: str
    ) -> Dict[str, Any]:
        """
        Check token balance for a specific user.

        Args:
            user_id: User identifier
            token: Token symbol to check balance for

        Returns:
            Dict containing:
                - success (bool): Whether the operation was successful
                - balance (float, optional): Token balance if successful
                - error (str, optional): Error message if operation failed
                - code (str, optional): Error code if operation failed
        """
        if not user_id or not token:
            error_msg = "User ID and token are required"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "MISSING_REQUIRED_FIELDS"
            }

        try:
            # Try primary service first
            service = self.services[self.primary_service]
            
            # Try direct balance check
            result = await self._get_balance_from_primary_service(service, user_id, token)
            if result:
                return result
            
            # Fall back to positions
            result = await self._get_balance_from_positions(service, user_id, token)
            if result:
                return result
            
            # Finally, fall back to GMGN
            return await self._get_balance_from_gmgn(user_id, token)
            
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid parameters for balance check: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "INVALID_PARAMETERS"
            }
        except (ConnectionError, TimeoutError) as e:
            error_msg = f"Failed to connect to balance service: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "BALANCE_CONNECTION_ERROR"
            }
        except Exception as e:  # pylint: disable=broad-except
            error_msg = f"Error checking {token} balance for user {user_id[-4:]}: {str(e)}"
            self.logger.exception(error_msg)
            return {
                "success": False,
                "error": "Failed to check token balance",
                "code": "BALANCE_CHECK_ERROR",
                "details": str(e)
            }
            
    async def check_wallet_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete wallet balance across all tokens.

        Args:
            user_id: User identifier

        Returns:
            Dict containing:
                - success (bool): Whether the operation was successful
                - balances (dict, optional): Dictionary of token balances if successful
                - error (str, optional): Error message if operation failed
                - code (str, optional): Error code if operation failed
        """
        try:
            # Try primary service first
            service = self.services[self.primary_service]
            
            # Try getting direct wallet balance first if available
            if hasattr(service, "get_wallet_balance"):
                try:
                    result = await service.get_wallet_balance(user_id)
                    if result.get("success", False):
                        self.logger.debug("Wallet balance retrieved successfully via %s for user %s",
                                 self.primary_service.value, user_id[-4:])
                        return result
                except Exception as e:
                    self.logger.error("Error retrieving wallet balance via %s for user %s: %s",
                             self.primary_service.value, user_id[-4:], str(e))
            
            # Fall back to getting positions if direct balance check fails
            try:
                positions = await service.get_user_positions(user_id)
                if positions.get("success", False):
                    # Process positions to extract balance information
                    return await self._process_positions_to_balances(positions, user_id)
                
                # If positions retrieval failed, fall back to GMGN
                self.logger.warning("Failed to get positions, falling back to GMGN")
                return await self._fallback_to_gmgn_wallet_balance(user_id)
                
            except Exception as e:
                self.logger.error("Error processing positions: %s", str(e))
                return await self._fallback_to_gmgn_wallet_balance(user_id)
            
        except (ValueError, KeyError) as e:
            error_msg = "Invalid parameters for wallet balance check: %s"
            self.logger.error(error_msg, str(e))
            return {
                "success": False,
                "error": error_msg % str(e),
                "code": "INVALID_PARAMETERS"
            }
        except (ConnectionError, TimeoutError) as e:
            error_msg = "Failed to connect to wallet service: %s"
            self.logger.error(error_msg, str(e))
            return {
                "success": False,
                "error": error_msg % str(e),
                "code": "WALLET_CONNECTION_ERROR"
            }
        except Exception as e:  # pylint: disable=broad-except
            error_msg = "Error retrieving wallet balance for user %s"
            self.logger.exception(error_msg, user_id[-4:])
            return {
                "success": False,
                "error": error_msg % user_id[-4:],
                "code": "WALLET_BALANCE_ERROR"
            }

    def get_service(self, service_type: TradingService) -> Any:
        """
        Get a specific trading service instance.

        Args:
            service_type: The type of trading service to retrieve

        Returns:
            The requested trading service instance or None if not found
        """
        return self.services.get(service_type)
        
    async def _fallback_to_gmgn_wallet_balance(self, user_id: str) -> Dict[str, Any]:
        """Handle fallback to GMGN service for wallet balance."""
        self.logger.info("Falling back to GMGN for complete wallet balance")
        gmgn_service = self.services[TradingService.GMGN]
        gmgn_result = await gmgn_service.get_wallet_balance(user_id)
        
        if gmgn_result.get("success", False):
            self.logger.debug(
                "Wallet balance retrieved successfully via GMGN for user %s",
                user_id[-4:])
        return gmgn_result
        
    async def _process_positions_to_balances(
        self, 
        positions: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """Convert positions data to wallet balances format."""
        balances = {}
        
        for position in positions.get("positions", []):
            symbol = position.get("symbol", "")
            if "/" not in symbol:
                continue
                
            base_token, quote_token = symbol.split("/", 1)
            size = position.get("size", 0)
            notional_value = position.get("notionalValue", 0)
            is_long = position.get("side", "").lower() == "long"
            
            # Initialize tokens in balances if not exists
            for token in (base_token, quote_token):
                if token not in balances:
                    balances[token] = {
                        "amount": 0.0,
                        "value_usd": 0.0,
                        "source": self.primary_service.value
                    }
            
            # Update balances based on position
            if is_long:
                balances[base_token]["amount"] += size
                balances[quote_token]["amount"] -= notional_value
            else:  # short position
                balances[base_token]["amount"] -= size
                balances[quote_token]["amount"] += notional_value
            
            # Update USD values
            balances[base_token]["value_usd"] = notional_value
        
        self.logger.debug(
            "Wallet balance compiled from %s positions for user %s",
            len(positions.get("positions", [])), user_id[-4:])
            
        return {
            "success": True,
            "balances": balances,
            "platform": self.primary_service.value
        }

    async def execute_leverage_trade(
            self,
            trade_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a leverage trade using primary service with fallback.
        
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
                "Executing leverage trade: %s %s %s with %sx leverage",
                side, size, market, leverage
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
                    self.logger.info(
                        "Leverage trade executed successfully via %s",
                        self.primary_service.value
                    )
                    return result
                
                error = result.get("error", "Unknown error")
                self.logger.warning(
                    "Leverage trade failed via %s: %s",
                    self.primary_service.value, error
                )
            else:
                self.logger.warning(
                    "%s doesn't support leverage trading directly",
                    self.primary_service.value
                )
            
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
                
        except (ValueError, KeyError) as e:
            error_msg = "Invalid leverage trade parameters: %s"
            self.logger.error(error_msg, str(e))
            return {
                "success": False,
                "error": error_msg % str(e),
                "code": "INVALID_PARAMETERS"
            }
        except (ConnectionError, TimeoutError) as e:
            error_msg = "Connection error executing leverage trade: %s"
            self.logger.error(error_msg, str(e))
            return {
                "success": False,
                "error": error_msg % str(e),
                "code": "LEVERAGE_TRADE_CONNECTION_ERROR"
            }
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid parameters for leverage trade: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "INVALID_LEVERAGE_PARAMS"
            }
        except (ConnectionError, TimeoutError) as e:
            error_msg = f"Connection error executing leverage trade: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": "Failed to connect to trading service",
                "code": "LEVERAGE_TRADE_CONNECTION_ERROR",
                "details": str(e)
            }
        except Exception as e:  # pylint: disable=broad-except
            error_msg = f"Unexpected error in leverage trade execution: {str(e)}"
            self.logger.exception(error_msg)
            return {
                "success": False,
                "error": "An unexpected error occurred during trade execution",
                "code": "LEVERAGE_TRADE_ERROR",
                "details": str(e)
            }
            
    async def confirm_trade(self, confirmation_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Confirm a pending trade execution using the primary service with fallback.
        
        Args:
            confirmation_id: The ID of the trade confirmation to process
            user_id: Optional user identifier
            
        Returns:
            Dict containing:
                - success (bool): Whether the operation was successful
                - error (str, optional): Error message if operation failed
                - code (str, optional): Error code if operation failed
        """
        if not confirmation_id:
            error_msg = "Confirmation ID is required"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "INVALID_PARAMETERS"
            }
            
        self.logger.info(
            "Confirming trade with ID: %s for user: %s",
            confirmation_id, user_id or "unknown"
        )
        
        try:
            # First try using the primary service (Mango V3)
            service = self.services[self.primary_service]
            
            # Check if the service has a confirm_trade method
            if hasattr(service, "confirm_trade"):
                self.logger.debug(
                    "Attempting trade confirmation via %s",
                    self.primary_service.value
                )
                result = await service.confirm_trade(confirmation_id, user_id=user_id)
                if result.get("success", False):
                    self.logger.info(
                        "Trade %s confirmed successfully via %s",
                        confirmation_id, self.primary_service.value
                    )
                    return result
                
                error = result.get("error", "Unknown error")
                self.logger.warning(
                    "Trade confirmation failed via %s: %s",
                    self.primary_service.value, error
                )
            else:
                self.logger.error("No service available for trade confirmation")
                return {
                    "success": False,
                    "error": "No service available for trade confirmation",
                    "code": "SERVICE_UNAVAILABLE"
                }
            
            # Fall back to GMGN service if primary fails or doesn't support confirmation
            gmgn_service = self.services[TradingService.GMGN]
            self.logger.info(
                "Falling back to GMGN for trade confirmation: %s",
                confirmation_id
            )
            
            if hasattr(gmgn_service, "confirm_trade"):
                try:
                    result = await gmgn_service.confirm_trade(confirmation_id, user_id=user_id)
                    
                    # Standardize response format
                    if "status" in result and "success" not in result:
                        result["success"] = result["status"] == "success"
                    
                    if result.get("success", False):
                        self.logger.info("Trade %s confirmed successfully via GMGN", confirmation_id)
                    else:
                        self.logger.warning(
                            "Trade confirmation failed via GMGN: %s",
                            result.get("error", "Unknown error")
                        )
                    
                    return result
                except Exception as e:  # pylint: disable=broad-except
                    error_msg = "Error during GMGN trade confirmation: %s"
                    self.logger.exception(error_msg, str(e))
                    return {
                        "success": False,
                        "error": error_msg % str(e),
                        "code": "GMGN_CONFIRMATION_ERROR",
                        "confirmation_id": confirmation_id,
                        "user_id": user_id
                    }
            
            error_msg = "No service available for trade confirmation"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "SERVICE_UNAVAILABLE",
                "confirmation_id": confirmation_id,
                "user_id": user_id
            }
                
        except (ValueError, KeyError) as e:
            error_msg = "Invalid trade confirmation parameters: %s"
            self.logger.error(error_msg, str(e))
            return {
                "success": False,
                "error": error_msg % str(e),
                "code": "INVALID_PARAMETERS",
                "confirmation_id": confirmation_id,
                "user_id": user_id
            }
        except (ConnectionError, TimeoutError) as e:
            error_msg = "Connection error confirming trade: %s"
            self.logger.error(error_msg, str(e))
            return {
                "success": False,
                "error": error_msg % str(e),
                "code": "CONNECTION_ERROR",
                "confirmation_id": confirmation_id,
                "user_id": user_id
            }
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid trade confirmation parameters: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "INVALID_CONFIRMATION_PARAMS",
                "confirmation_id": confirmation_id,
                "user_id": user_id
            }
        except (ConnectionError, TimeoutError) as e:
            error_msg = f"Connection error confirming trade: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": "Failed to connect to trade confirmation service",
                "code": "CONFIRMATION_CONNECTION_ERROR",
                "confirmation_id": confirmation_id,
                "user_id": user_id,
                "details": str(e)
            }
        except Exception as e:  # pylint: disable=broad-except
            error_msg = f"Unexpected error confirming trade {confirmation_id}: {str(e)}"
            self.logger.exception(error_msg)
            return {
                "success": False,
                "error": "An unexpected error occurred while confirming the trade",
                "code": "CONFIRMATION_ERROR",
                "confirmation_id": confirmation_id,
                "user_id": user_id,
                "details": str(e)
            }
            
    async def modify_leverage_position(
        self,
        position_id: str,
        modification_type: str,
        new_value: Any,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify an existing leverage position.
        
        Args:
            position_id: Position identifier
            modification_type: Type of modification (tp, sl, size, leverage)
            new_value: New value for the modification
            user_id: Optional user identifier
                
        Returns:
            Dict containing:
                - success (bool): Whether the operation was successful
                - error (str, optional): Error message if operation failed
                - code (str, optional): Error code if operation failed
                - details (str, optional): Additional error details
        """
        if not position_id or not modification_type:
            error_msg = "Position ID and modification type are required"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "INVALID_PARAMETERS"
            }
        try:
            # Try primary service first
            service = self.services[self.primary_service]
            
            try:
                if hasattr(service, "modify_position"):
                    result = await service.modify_position(
                        position_id=position_id,
                        modification_type=modification_type,
                        new_value=new_value,
                        user_id=user_id
                    )
                    
                    if result.get("success", False):
                        self.logger.info(
                            "Position %s modified successfully via %s",
                            position_id, self.primary_service.value
                        )
                        return result
                    
                    error = result.get("error", "Unknown error")
                    self.logger.warning(
                        "Position modification failed via %s: %s",
                        self.primary_service.value, error
                    )
                else:
                    self.logger.warning(
                        "Primary service doesn't support position modification"
                    )
            except (ValueError, KeyError) as e:
                error_msg = f"Invalid parameters for position modification: {str(e)}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "code": "INVALID_MODIFICATION_PARAMS"
                }
            except (ConnectionError, TimeoutError) as e:
                error_msg = f"Connection error modifying position: {str(e)}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": "Failed to connect to position service",
                    "code": "POSITION_MODIFICATION_CONNECTION_ERROR",
                    "details": str(e)
                }
            
            # Fall back to GMGN
            gmgn_service = self.services[TradingService.GMGN]
            self.logger.info("Falling back to GMGN for position modification")
            
            try:
                if hasattr(gmgn_service, "modify_leverage_position"):
                    result = await gmgn_service.modify_leverage_position(
                        position_id=position_id,
                        modification_type=modification_type,
                        new_value=new_value,
                        user_id=user_id
                    )
                    
                    if result.get("success", False):
                        self.logger.info(
                            "Position %s modified successfully via GMGN",
                            position_id
                        )
                        return result
                        
                    error = result.get("error", "Unknown error")
                    self.logger.warning(
                        "Position modification failed via GMGN: %s",
                        error
                    )
                    return {
                        "success": False,
                        "error": error,
                        "code": "POSITION_MODIFICATION_FAILED"
                    }
                
                error_msg = "GMGN service doesn't support position modification"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "code": "FUNCTIONALITY_NOT_SUPPORTED"
                }
                
            except (ValueError, KeyError) as e:
                error_msg = f"Invalid parameters for GMGN position modification: {str(e)}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "code": "INVALID_GMGN_PARAMETERS"
                }
            except (ConnectionError, TimeoutError) as e:
                error_msg = f"GMGN connection error modifying position: {str(e)}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": "Failed to connect to GMGN service",
                    "code": "GMGN_CONNECTION_ERROR",
                    "details": str(e)
                }
            except Exception as e:  # pylint: disable=broad-except
                error_msg = f"Unexpected error in GMGN position modification: {str(e)}"
                self.logger.exception(error_msg)
                return {
                    "success": False,
                    "error": "An unexpected error occurred while modifying the position via GMGN",
                    "code": "GMGN_POSITION_MODIFICATION_ERROR",
                    "details": str(e)
                }
                
            error_msg = "No service available for position modification"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "SERVICE_UNAVAILABLE"
            }
            
        except Exception as e:  # pylint: disable=broad-except
            error_msg = f"Unexpected error in position modification: {str(e)}"
            self.logger.exception(error_msg)
            return {
                "success": False,
                "error": "An unexpected error occurred during position modification",
                "code": "POSITION_MODIFICATION_ERROR",
                "details": str(e)
            }
            
    async def close_position(
        self,
        market_name: str,
        position_id: Optional[str] = None,
        size: Optional[float] = None,
        price: float = 0,  # 0 for market order
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # pylint: disable=too-many-arguments,too-many-locals
        """
        Close an existing position according to the Mango v3 documentation.
        
        Args:
            market_name: The market name (e.g., "BTC/USDC")
            position_id: Optional position ID (if not provided, will find by market)
            size: Amount to close (if None, closes entire position)
            price: Limit price (0 for market orders)
            user_id: User ID for tracking
            
        Returns:
            Dict containing:
                - success (bool): Whether the operation was successful
                - error (str, optional): Error message if operation failed
                - code (str, optional): Error code if operation failed
                - details (str, optional): Additional error details
        """
        if not market_name and not position_id:
            error_msg = "Either market_name or position_id must be provided"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "INVALID_PARAMETERS"
            }
        position_identifier = position_id or market_name
        self.logger.info(
            "Attempting to close position: %s (size: %s, price: %s)",
            position_identifier, size or "all", price or "market"
        )
        
        try:
            # Try primary service first
            service = self.services[self.primary_service]
            
            try:
                if hasattr(service, "close_position"):
                    result = await service.close_position(
                        market_name=market_name,
                        position_id=position_id,
                        size=size,
                        price=price,
                        user_identifier=user_id
                    )
                    
                    if result.get("success", False):
                        self.logger.info(
                            "Position %s closed successfully via %s",
                            position_identifier,
                            self.primary_service.value
                        )
                        return result
                    
                    error = result.get("error", "Unknown error")
                    self.logger.warning(
                        "Position %s closing failed via %s: %s",
                        position_identifier,
                        self.primary_service.value,
                        error
                    )
                else:
                    self.logger.warning(
                        "Primary service doesn't support position closing"
                    )
            except (ValueError, KeyError) as e:
                error_msg = f"Invalid parameters for position closing: {str(e)}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "code": "INVALID_CLOSE_PARAMETERS",
                    "position": position_identifier
                }
            except (ConnectionError, TimeoutError) as e:
                error_msg = f"Connection error closing position: {str(e)}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": "Failed to connect to trading service",
                    "code": "POSITION_CLOSE_CONNECTION_ERROR",
                    "details": str(e),
                    "position": position_identifier
                }
            
            # Fall back to GMGN
            gmgn_service = self.services[TradingService.GMGN]
            self.logger.info(
                "Falling back to GMGN for position %s closing",
                position_identifier
            )
            
            try:
                if hasattr(gmgn_service, "close_position"):
                    gmgn_args = {
                        "market_name": market_name,
                        "position_id": position_id,
                        "size": size,
                        "price": price,
                        "user_id": user_id
                    }
                    gmgn_result = await gmgn_service.close_position(**gmgn_args)
                    
                    if gmgn_result.get("success", False):
                        self.logger.info(
                            "Position %s closed successfully via GMGN",
                            position_identifier
                        )
                    return gmgn_result
                
                error_msg = "GMGN service doesn't support position closing"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "code": "FUNCTIONALITY_NOT_SUPPORTED",
                    "position": position_identifier
                }
            except (ValueError, KeyError) as e:
                error_msg = f"Invalid parameters for GMGN position closing: {str(e)}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "code": "INVALID_GMGN_PARAMETERS",
                    "position": position_identifier
                }
            except (ConnectionError, TimeoutError) as e:
                error_msg = f"GMGN connection error closing position: {str(e)}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": "Failed to connect to GMGN service",
                    "code": "GMGN_CONNECTION_ERROR",
                    "details": str(e),
                    "position": position_identifier
                }
            except Exception as e:  # pylint: disable=broad-except
                error_msg = f"Unexpected error in GMGN position closing: {str(e)}"
                self.logger.exception(error_msg)
                return {
                    "success": False,
                    "error": "An unexpected error occurred while closing the position via GMGN",
                    "code": "GMGN_POSITION_CLOSE_ERROR",
                    "details": str(e),
                    "position": position_identifier
                }
            
        except Exception as e:
            error_msg = f"Unexpected error closing position {position_identifier}: {str(e)}"
            self.logger.exception(error_msg)
            return {
                "success": False,
                "error": "An unexpected error occurred while closing the position",
                "code": "POSITION_CLOSE_ERROR",
                "details": str(e),
                "position": position_identifier
            }
            
    async def sell_spot_token(
        self,
        token: str,
        amount: float,
        target_token: str = "USDC",
        price: float = 0,  # 0 for market order
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # pylint: disable=too-many-arguments
        """
        Sell a spot token according to the Mango v3 documentation.
        
        Args:
            token: Token to sell (e.g., "BTC")
            amount: Amount to sell
            target_token: Token to receive (default: "USDC")
            price: Limit price (0 for market orders)
            user_id: User ID for tracking
            
        Returns:
            Dict containing:
                - success (bool): Whether the operation was successful
                - error (str, optional): Error message if operation failed
                - code (str, optional): Error code if operation failed
        """
        try:
            self.logger.info(
                "Selling %s %s for %s via %s",
                amount, token, target_token, self.primary_service.value
            )
            
            # Try primary service first
            service = self.services[self.primary_service]
            
            if hasattr(service, "sell_spot_token"):
                result = await service.sell_spot_token(
                    token=token,
                    amount=amount,
                    target_token=target_token,
                    price=price,
                    user_id=user_id
                )
                
                if result.get("success", False):
                    self.logger.info(
                        "Spot token %s sold successfully via %s",
                        token, self.primary_service.value
                    )
                    return result
                
                error = result.get("error", "Unknown error")
                self.logger.warning(
                    "Spot token %s sale failed via %s: %s",
                    token, self.primary_service.value, error
                )
            
            # Fall back to GMGN
            gmgn_service = self.services[TradingService.GMGN]
            self.logger.info(
                "Falling back to GMGN for %s spot token sale",
                token
            )
            
            if hasattr(gmgn_service, "sell_spot_token"):
                gmgn_result = await gmgn_service.sell_spot_token(
                    token=token,
                    amount=amount,
                    target_token=target_token,
                    price=price,
                    user_id=user_id
                )
                
                if gmgn_result.get("success", False):
                    self.logger.info(
                        "Spot token %s sold successfully via GMGN",
                        token
                    )
                return gmgn_result
            
            error_msg = "No service available for spot token sale"
            self.logger.error("%s: %s", error_msg, token)
            return {
                "success": False,
                "error": error_msg,
                "code": "SERVICE_UNAVAILABLE"
            }
            
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid spot token sale parameters: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "code": "INVALID_PARAMETERS"
            }
        except Exception as e:  # pylint: disable=broad-except
            error_msg = "Unexpected error during spot token sale"
            self.logger.exception("%s: %s", error_msg, str(e))
            return {
                "success": False,
                "error": error_msg,
                "code": "SPOT_TOKEN_SALE_ERROR"
            }
