"""
Trading Service Selector for Grace

This module provides a non-invasive way to select and manage trading services.
GMGN is the primary and only spot trading service used for initiating trades.
It returns Phantom-signable payloads for client-side signing.
"""

import logging
import time
from typing import Dict, Any, Optional
import asyncio
from enum import Enum

# Local imports

try:
    from .gmgn_service import GMGNService
except ImportError:
    from gmgn_service import GMGNService

# Optional Flash helper client
try:
    from .adapters.flash.flash_helper_client import FlashHelperClient  # type: ignore
except Exception:  # pragma: no cover
    try:
        from adapters.flash.flash_helper_client import FlashHelperClient  # type: ignore
    except Exception:  # pragma: no cover
        FlashHelperClient = None  # type: ignore

# Leverage manager (uses Flash flows already)
try:
    from .leverage_trading_handler import LeverageTradeManager  # type: ignore
except Exception:  # pragma: no cover
    try:
        from leverage_trading_handler import LeverageTradeManager  # type: ignore
    except Exception:
        LeverageTradeManager = None  # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
_LOGGER = logging.getLogger("TradingServiceSelector")


class TradingService(Enum):
    """Available trading services."""

    GMGN = "gmgn"


class TradingServiceSelector:
    """
    Manages trading service selection and fallback logic.
    Non-invasive implementation that preserves existing functionality.
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
        gmgn_config = self.config.get("gmgn", {})
        gmgn_config["logger"] = self.logger
        
        # Initialize services
        try:
            self.services = {
                TradingService.GMGN: GMGNService(
                    config=gmgn_config,
                    memory_system=memory_system
                ),
            }
            # Set GMGN as the primary service moving forward
            self.primary_service = TradingService.GMGN
            self.logger.info(
                "Trading services initialized with primary: %s",
                self.primary_service.value
            )
            # Optional Flash client for direct helper calls
            self.flash_client = None
            use_client = str(self.config.get("FLASH_USE_CLIENT") or "").lower() in ("1", "true", "yes")
            if FlashHelperClient is not None and use_client:
                try:
                    self.flash_client = FlashHelperClient()
                    self.logger.info("FlashHelperClient enabled in TradingServiceSelector")
                except Exception as e:  # pragma: no cover
                    self.logger.warning(f"Failed to init FlashHelperClient in selector: {e}")

            # Optional leverage manager for Flash auto loops
            self.leverage_manager = None
            if LeverageTradeManager is not None:
                try:
                    self.leverage_manager = LeverageTradeManager(
                        gmgn_service=self.services[TradingService.GMGN],
                        memory_system=memory_system,
                        logger=self.logger,
                    )
                except Exception as e:  # pragma: no cover
                    self.logger.warning(f"Failed to init LeverageTradeManager: {e}")
            self._flash_monitor_task = None
        except Exception as e:
            self.logger.exception(
                "Failed to initialize trading services: %s",
                str(e)
            )
            raise RuntimeError("Failed to initialize trading services") from e

    # --- Flash wiring: thin wrappers and monitoring ---
    def has_flash_client(self) -> bool:
        return getattr(self, "flash_client", None) is not None

    async def get_flash_prices(self) -> Dict[str, Any]:
        if not self.has_flash_client():
            return {"success": False, "error": "Flash client not enabled"}
        loop = asyncio.get_running_loop()
        try:
            data = await loop.run_in_executor(None, self.flash_client.get_prices)  # type: ignore[attr-defined]
            return data if isinstance(data, dict) else {"success": False, "error": "Invalid response"}
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Flash get_prices error: {e}")
            return {"success": False, "error": str(e)}

    async def get_flash_positions(self) -> Dict[str, Any]:
        if not self.has_flash_client():
            return {"success": False, "error": "Flash client not enabled"}
        loop = asyncio.get_running_loop()
        try:
            data = await loop.run_in_executor(None, self.flash_client.get_positions)  # type: ignore[attr-defined]
            return data if isinstance(data, dict) else {"success": False, "error": "Invalid response"}
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Flash get_positions error: {e}")
            return {"success": False, "error": str(e)}

    async def start_flash_auto_monitoring(self, poll_interval: float = 5.0) -> Dict[str, Any]:
        """
        Start a background loop to monitor Flash prices/positions and invoke leverage manager execution
        with the same safety and risk measures used for auto-traded spot (GMGN) flows.
        """
        if self._flash_monitor_task and not self._flash_monitor_task.done():
            return {"success": True, "message": "Flash monitoring already running"}
        if not self.leverage_manager:
            return {"success": False, "error": "LeverageTradeManager unavailable"}
        self._flash_monitor_task = asyncio.create_task(self._flash_monitor_loop(poll_interval))
        return {"success": True}

    async def stop_flash_auto_monitoring(self) -> Dict[str, Any]:
        task = getattr(self, "_flash_monitor_task", None)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        return {"success": True}

    async def _flash_monitor_loop(self, poll_interval: float) -> None:
        self.logger.info("Starting Flash auto-monitoring loop (interval=%ss)", poll_interval)
        try:
            while True:
                try:
                    # Fetch prices via leverage manager (which uses Flash client if enabled)
                    prices_data = self.leverage_manager.flash_get_prices() if self.leverage_manager else {"success": False}
                    market_prices: Dict[str, float] = {}
                    if prices_data.get("success"):
                        for sym, info in (prices_data.get("prices", {}) or {}).items():
                            try:
                                exp = int(info.get("exponent", 0))
                                val = info.get("emaPrice") or info.get("price")
                                if val is not None:
                                    price = float(val) * (10 ** exp)
                                    market_prices[f"{sym.upper()}-PERP"] = price
                            except Exception:
                                continue
                    # Execute leverage trade logic with risk controls
                    if self.leverage_manager and market_prices:
                        _ = self.leverage_manager.execute_trades(market_prices)
                except Exception as inner:
                    self.logger.debug(f"Flash monitor iteration error: {inner}")
                await asyncio.sleep(poll_interval)
        except asyncio.CancelledError:
            self.logger.info("Flash auto-monitoring loop cancelled")
            raise

    async def setup_auto_trading(
        self,
        user_id: str,
        risk_level: str,
        max_trade_size: float,
        stop_loss: float,
        take_profit: float,
        wallet_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pass-through setup for auto trading to the primary service (GMGN).

        This bridges to the synchronous GMGNService.setup_auto_trading using
        an executor so the selector remains usable in async contexts.
        """
        try:
            service = self.services[self.primary_service]
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None,
                lambda: service.setup_auto_trading(
                    user_id=user_id,
                    risk_level=risk_level,
                    max_trade_size=max_trade_size,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    wallet_address=wallet_address,
                ),
            )
        except Exception as e:  # pylint: disable=broad-except
            self.logger.exception("Auto-trading setup failed via selector: %s", str(e))
            return {
                "success": False,
                "error": "Failed to setup auto trading",
                "code": "AUTO_TRADING_SELECTOR_ERROR",
                "details": str(e),
            }

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
            # Prepare parameters expected by GMGN
            action = (trade_params.get("action") or trade_params.get("side") or "buy").lower()
            token = (
                trade_params.get("token")
                or trade_params.get("symbol")
                or trade_params.get("to_token")
                or trade_params.get("market")
            )
            amount_value = trade_params.get("amount") or trade_params.get("size")
            amount = str(amount_value) if amount_value is not None else None
            user_id = trade_params.get("user_id")
            wallet_address = trade_params.get("wallet_address")

            if not token or not amount or not user_id:
                raise ValueError("user_id, token, and amount are required for trade initiation")

            # Use GMGN to build a Phantom-signable payload. Bridge sync call via executor.
            service = self.services[self.primary_service]
            loop = asyncio.get_running_loop()

            if hasattr(service, "build_unsigned_spot_transaction"):
                result = await loop.run_in_executor(
                    None,
                    lambda: service.build_unsigned_spot_transaction(
                        action=action,
                        amount=amount,
                        token=token,
                        wallet_address=wallet_address,
                        user_id=user_id,
                    ),
                )
                return result

            # Fallback: use GMGN execute_trade to return confirmation info
            result = await loop.run_in_executor(
                None,
                lambda: service.execute_trade(
                    action=action, amount=amount, token=token, user_id=user_id
                ),
            )
            return result
            
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
            # Try primary service (GMGN)
            service = self.services[self.primary_service]
            # Bridge sync methods if needed
            if hasattr(service, "get_market_data") and asyncio.iscoroutinefunction(service.get_market_data):
                result = await service.get_market_data(market)
            else:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, lambda: service.get_market_data(market))
            
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
            
            # No other services; return the result we have
            return result
            
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
