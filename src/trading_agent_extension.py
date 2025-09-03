"""
Trading Agent Extension for Grace

This module extends the TradingAgent focusing on GMGN/Flash integration.
Leverage trading is handled via Flash (unsigned transaction prompt flow),
and spot/trade utilities remain GMGN-compatible.
"""

import datetime
import logging
import time
import os
from typing import Dict, Any, Optional
from src.agent_framework import AgentTask, TradingAgent
from src.trading_service_selector import TradingServiceSelector, TradingService

# Configure logging
logger = logging.getLogger("EnhancedTradingAgent")


class EnhancedTradingAgent(TradingAgent):
    """
    Enhanced Trading Agent with GMGN + Flash integration.
    Leverage trading routes to Flash via LeverageTradeManager.
    """

    def __init__(self, agent_id="enhanced_trading_agent", api_services_manager=None, 
                 memory_system=None, task_queue=None, result_queue=None, config=None, **kwargs):
        """Initialize enhanced trading agent with full TradingAgent compatibility.
        
        Args:
            agent_id: Unique identifier for the agent
            api_services_manager: API services manager
            memory_system: Memory system
            task_queue: Queue for incoming tasks
            result_queue: Queue for task results
            config: Agent configuration
            **kwargs: Additional keyword arguments
        """
        # Initialize logger first
        self.logger = logging.getLogger(f"EnhancedTradingAgent.{agent_id}")
        
        # Initialize base TradingAgent with all parameters
        try:
            super().__init__(
                agent_id=agent_id,
                api_services_manager=api_services_manager,
                memory_system=memory_system,
                task_queue=task_queue,
                result_queue=result_queue,
                config=config,
                **kwargs
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize base TradingAgent: {str(e)}", exc_info=True)
            raise
        
        # Log agent initialization
        self.logger.info(f"Initializing EnhancedTradingAgent with ID: {agent_id}")
        
        # Initialize service selector with proper logging
        try:
            # Initialize service selector with proper configuration
            self.service_selector = TradingServiceSelector(
                config=self.config,
                memory_system=self.memory_system,
                logger=self.logger
            )
            self.logger.info("TradingServiceSelector initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TradingServiceSelector: {str(e)}", exc_info=True)
            raise
        
        # Add additional supported task types specific to enhanced operations
        self.supported_task_types.extend([
            "execute_swap",
            "trade_preparation",
            "monitor_smart_trading",
            "execute_leverage_trade",
            "modify_leverage_position"
        ])
        
        # Initialize connection to leverage trading handler if available
        try:
            from src.leverage_trading_handler import LeverageTradeManager
            self.leverage_manager = None
            
            if hasattr(self.config, 'get') and self.config.get('leverage_trading', {}).get('enabled', True):
                self.logger.info("Initializing connection to leverage trading handler")
                try:
                    self.leverage_manager = LeverageTradeManager(
                        gmgn_service=getattr(self, 'gmgn_service', None),
                        memory_system=self.memory_system,
                        logger=self.logger,
                        **self.config.get('leverage_trading', {})
                    )
                except Exception as e:
                    self.logger.error(
                        f"Failed to initialize Leverage Trade Manager: {str(e)}",
                        exc_info=True
                    )
                    self.leverage_manager = None
        except ImportError:
            self.logger.warning("Leverage trading handler not available")
            self.leverage_manager = None
            
        # Transaction deduplication cache to prevent double execution
        self.transaction_cache = {}
        self.transaction_cache_ttl = 300  # 5 minutes TTL for transaction IDs

    async def _handle_execute_trade(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle trade execution using Mango V3 with GMGN fallback.

        Args:
            task: Trade task to process

        Returns:
            Trade result dictionary
        """
        # Mark task as in-progress immediately
        task.status = "in_progress"
        task.started_at = datetime.datetime.now()

        # Validate required parameters
        required_params = ["market", "side", "size"]
        missing_params = [
            param for param in required_params if not task.content.get(param)
        ]

        if missing_params:
            error_msg = f"Missing required parameters: {', '.join(missing_params)}"
            self.logger.error(f"Trade validation failed: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}

        try:
            # Extract user_id for wallet balance check
            user_id = task.content.get("user_id")
            client_id = task.content.get("client_id", task.task_id)
            
            # Check for duplicate transaction - prevent double execution
            transaction_key = f"{client_id}_{task.task_id}"
            if transaction_key in self.transaction_cache:
                self.logger.warning(f"Duplicate trade detected: {transaction_key} - preventing double execution")
                cached_result = self.transaction_cache[transaction_key]
                task.status = "completed"
                task.result = cached_result
                task.completed_at = datetime.datetime.now()
                return cached_result
            
            # Prepare trade parameters in Mango format
            trade_params = {
                "market": task.content.get("market", ""),
                "side": task.content.get("side", "buy"),
                "type": task.content.get("type", "market"),
                "size": float(task.content.get("size", 0)),
                "price": (
                    float(task.content.get("price", 0))
                    if task.content.get("price")
                    else None
                ),
                "user_id": user_id,
                "client_id": client_id
            }
            
            # Log the trade attempt
            self.logger.info(
                f"Trade execution attempt: {trade_params['side']} {trade_params['size']} {trade_params['market']} "
                f"via {task.content.get('service', 'default')}"
            )
            
            # First check wallet balance if user_id is provided
            if user_id:
                self.logger.info(f"Checking wallet balance for user {user_id} before execution")
                balance_check = await self.service_selector.check_wallet_balance(user_id)
                
                if not balance_check.get("success", False):
                    error_msg = balance_check.get("error", "Failed to check wallet balance")
                    self.logger.warning(f"Wallet balance check failed: {error_msg}")
                else:
                    # Extract balance information for logging
                    balances = balance_check.get("balances", {})
                    self.logger.info(f"Mango V3 wallet balances: {balances}")
                    
                    # Now check internal wallet balance
                    internal_balances = await self._get_internal_wallet_balance(user_id)
                    self.logger.info(f"Internal wallet balances: {internal_balances}")
                    
                    # Determine required token and amount based on trade parameters
                    market = trade_params.get("market", "")
                    side = trade_params.get("side", "")
                    size = float(trade_params.get("size", 0))
                    
                    # Parse market to get tokens
                    if "/" in market:
                        base_token, quote_token = market.split("/")
                    else:
                        base_token = market
                        quote_token = "USDC"  # Default quote token
                    
                    # For buy orders, we need quote token (usually USDC)
                    # For sell orders, we need base token (the asset being sold)
                    required_token = quote_token if side.lower() == "buy" else base_token
                    required_amount = size
                    
                    # If buying, calculate required USDC based on current price
                    if side.lower() == "buy":
                        try:
                            # Get current price
                            price_info = await self.service_selector.get_token_price(base_token)
                            if price_info and price_info.get("success"):
                                price = float(price_info.get("price", 0))
                                if price > 0:
                                    required_amount = size * price * 1.01  # Add 1% buffer for slippage
                        except Exception as e:
                            self.logger.warning(f"Error calculating required USDC: {str(e)}")
                    
                    # Check if Mango V3 wallet has enough balance
                    mango_balance = 0
                    for token_name, token_data in balances.items():
                        if token_name.lower() == required_token.lower():
                            mango_balance = float(token_data.get("amount", 0))
                            break
                    
                    # Check if internal wallet has enough balance
                    internal_balance = float(internal_balances.get(required_token.lower(), 0))
                    
                    self.logger.info(f"Required for trade: {required_amount} {required_token}")
                    self.logger.info(f"Available in Mango V3: {mango_balance} {required_token}")
                    self.logger.info(f"Available in internal: {internal_balance} {required_token}")
                    
                    # If Mango V3 doesn't have enough but internal does, transfer funds
                    if mango_balance < required_amount and internal_balance >= required_amount:
                        transfer_amount = required_amount - mango_balance
                        self.logger.info(f"Transferring {transfer_amount} {required_token} from internal wallet to Mango V3")
                        
                        # Execute the transfer
                        transfer_success = await self._transfer_from_internal_to_mango(
                            user_id=user_id,
                            token=required_token,
                            amount=transfer_amount
                        )
                        
                        if transfer_success:
                            self.logger.info(f"Successfully transferred funds for trading")
                        else:
                            self.logger.warning(f"Failed to transfer funds - trade may fail")
                    
                    # If neither wallet has enough, log a warning
                    elif mango_balance < required_amount and internal_balance < required_amount:
                        self.logger.warning(
                            f"Insufficient funds for trade. Required: {required_amount} {required_token}, "
                            f"Mango: {mango_balance}, Internal: {internal_balance}"
                        )
            
            # Execute via service selector
            result = await self.service_selector.execute_trade(trade_params)

            # Update task status
            if result.get("success", False):
                self.logger.info(f"Trade executed successfully: {task.task_id}")
                task.status = "completed"
                task.result = result
                
                # Cache successful result to prevent double execution
                transaction_key = f"{client_id}_{task.task_id}"
                self.transaction_cache[transaction_key] = result
                
                # Clean up old cache entries
                current_time = time.time()
                self.transaction_cache = {k: v for k, v in self.transaction_cache.items() 
                                         if k.split('_')[0] > str(current_time - self.transaction_cache_ttl)}
                
                # Synchronize balances with internal wallet
                await self._sync_balances_to_internal_wallet(user_id, result)
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.warning(f"Trade failed: {error_msg}")
                task.status = "failed"
                task.error = error_msg

            # Set completion timestamp
            task.completed_at = datetime.datetime.now()

            # Add task_id to result for better tracking
            if isinstance(result, dict):
                result["task_id"] = task.task_id
            else:
                result = {"success": True, "result": result, "task_id": task.task_id}

            return result

        except ValueError as ve:
            # Handle value errors (typically parameter conversion issues)
            error_msg = f"Invalid parameter value: {str(ve)}"
            self.logger.error(f"Trade parameter error: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in trade execution: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}

    async def _handle_trade_initiate(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle initial GMGN spot trade initiation with validation and routing via TradingServiceSelector.

        This is a lighter-weight path than _handle_execute_trade and is intended for initiating
        spot orders (market/limit) with minimal pre-processing.
        """
        # Mark task as in-progress
        task.status = "in_progress"
        task.started_at = datetime.datetime.now()

        # Validate required parameters
        required_params = ["market", "side", "size"]
        missing_params = [p for p in required_params if not task.content.get(p)]
        if missing_params:
            error_msg = f"Missing required parameters: {', '.join(missing_params)}"
            self.logger.error(f"trade_initiate validation failed: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}

        try:
            user_id = task.content.get("user_id")
            client_id = task.content.get("client_id", task.task_id)

            # Deduplicate by client_id + task_id
            transaction_key = f"{client_id}_{task.task_id}"
            if transaction_key in self.transaction_cache:
                self.logger.warning(
                    f"Duplicate trade_initiate detected: {transaction_key} - returning cached result"
                )
                cached_result = self.transaction_cache[transaction_key]
                task.status = "completed"
                task.result = cached_result
                task.completed_at = datetime.datetime.now()
                return cached_result

            # Build trade params
            trade_params: Dict[str, Any] = {
                "market": task.content.get("market", ""),
                "side": task.content.get("side", "buy"),
                "type": task.content.get("type", "market"),
                "size": float(task.content.get("size", 0)),
                "user_id": user_id,
                "client_id": client_id,
            }
            if task.content.get("price") is not None:
                trade_params["price"] = float(task.content.get("price"))

            self.logger.info(
                f"[trade_initiate] {trade_params['side']} {trade_params['size']} {trade_params['market']} "
                f"(type={trade_params.get('type','market')}) for user {str(user_id)[-4:] if user_id else 'anon'}"
            )

            # Execute via service selector (GMGN primary)
            result = await self.service_selector.execute_trade(trade_params)

            # Update task status and cache
            if result.get("success", False):
                task.status = "completed"
                task.result = result
                # Cache to prevent duplicate execution
                self.transaction_cache[transaction_key] = result
            else:
                task.status = "failed"
                task.error = result.get("error", "Unknown error")

            task.completed_at = datetime.datetime.now()

            # Include task_id in result for tracking
            if isinstance(result, dict):
                result["task_id"] = task.task_id
            else:
                result = {"success": True, "result": result, "task_id": task.task_id}

            return result

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in trade_initiate: {error_msg}", exc_info=True)
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}
            
    async def _handle_execute_swap(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle token swap execution using Mango V3 with GMGN fallback.
        
        Args:
            task: Swap task to process
            
        Returns:
            Swap result dictionary
        """
        # Mark task as in-progress
        task.status = "in_progress"
        task.started_at = datetime.datetime.now()
        
        # Validate required parameters
        required_params = ["from_token", "to_token", "amount"]
        missing_params = [param for param in required_params if not task.content.get(param)]
        
        if missing_params:
            error_msg = f"Missing required swap parameters: {', '.join(missing_params)}"
            self.logger.error(f"Swap validation failed: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}
        
        try:
            # Format swap parameters for service selector
            swap_params = {
                "from_token": task.content.get("from_token"),
                "to_token": task.content.get("to_token"),
                "amount": float(task.content.get("amount")),
                "user_id": task.content.get("user_id"),
                "client_id": task.task_id,
                "slippage": float(task.content.get("slippage", 1.0)),  # Default 1% slippage
            }
            
            # Log swap attempt
            self.logger.info(
                f"Swap execution attempt: {swap_params['amount']} {swap_params['from_token']} → "
                f"{swap_params['to_token']} with {swap_params['slippage']}% slippage"
            )
            
            # Execute via service selector - route to execute_swap method
            result = await self.service_selector.execute_swap(swap_params)
            
            # Update task status based on result
            if result.get("success", False):
                self.logger.info(f"Swap executed successfully: {task.task_id}")
                task.status = "completed"
                task.result = result
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.warning(f"Swap failed: {error_msg}")
                task.status = "failed"
                task.error = error_msg
                
            # Set completion timestamp
            task.completed_at = datetime.datetime.now()
            
            # Add task_id to result
            if isinstance(result, dict):
                result["task_id"] = task.task_id
            else:
                result = {"success": True, "result": result, "task_id": task.task_id}
                
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in swap execution: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}
    
    async def _handle_trade_preparation(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle trade preparation tasks (pre-trade validation, balance checks, etc).
        
        Args:
            task: Trade preparation task
            
        Returns:
            Trade preparation result dictionary
        """
        # Mark task as in-progress
        task.status = "in_progress"
        task.started_at = datetime.datetime.now()
        
        try:
            # Extract trade parameters
            market = task.content.get("market", "")
            side = task.content.get("side", "buy")
            size = float(task.content.get("size", 0))
            user_id = task.content.get("user_id")
            
            self.logger.info(f"Preparing trade: {side} {size} {market} for user {user_id}")
            
            # Validate wallet balance first
            balance_check = await self.service_selector.check_wallet_balance(user_id)
            
            if not balance_check.get("success", False):
                error_msg = balance_check.get("error", "Failed to check wallet balance")
                self.logger.warning(f"Trade preparation failed - balance check: {error_msg}")
                task.status = "failed"
                task.error = error_msg
                task.completed_at = datetime.datetime.now()
                return {"success": False, "error": error_msg, "task_id": task.task_id}
            
            # Extract balance information
            balances = balance_check.get("balances", {})
            
            # Determine required token based on side
            if "/" in market:
                base_token, quote_token = market.split("/")
                required_token = quote_token if side.lower() == "buy" else base_token
            else:
                # Default to USDC for buy orders if market format is unclear
                required_token = "USDC" if side.lower() == "buy" else market
            
            # Check if user has enough balance
            required_token_balance = float(balances.get(required_token, {}).get("amount", 0))
            
            if required_token_balance < size and side.lower() == "sell":
                error_msg = f"Insufficient {required_token} balance for trade. Available: {required_token_balance}, Required: {size}"
                self.logger.warning(f"Trade preparation failed - insufficient balance: {error_msg}")
                task.status = "failed"
                task.error = error_msg
                task.completed_at = datetime.datetime.now()
                return {"success": False, "error": error_msg, "task_id": task.task_id}
            
            # For buy orders, check USDC balance and estimate required amount
            if side.lower() == "buy":
                # Get current price
                price_check = await self.service_selector.get_token_price(market)
                if not price_check.get("success", False):
                    error_msg = price_check.get("error", "Failed to get token price")
                    self.logger.warning(f"Trade preparation failed - price check: {error_msg}")
                    task.status = "failed"
                    task.error = error_msg
                    task.completed_at = datetime.datetime.now()
                    return {"success": False, "error": error_msg, "task_id": task.task_id}
                
                # Get price and calculate required USDC
                price = float(price_check.get("price", 0))
                required_usdc = price * size * 1.01  # Add 1% buffer for slippage
                
                usdc_balance = float(balances.get("USDC", {}).get("amount", 0))
                
                if usdc_balance < required_usdc:
                    error_msg = f"Insufficient USDC balance for trade. Available: {usdc_balance}, Required: {required_usdc}"
                    self.logger.warning(f"Trade preparation failed - insufficient USDC: {error_msg}")
                    task.status = "failed"
                    task.error = error_msg
                    task.completed_at = datetime.datetime.now()
                    return {"success": False, "error": error_msg, "task_id": task.task_id}
            
            # All validations passed
            self.logger.info(f"Trade preparation successful for {side} {size} {market}")
            task.status = "completed"
            task.completed_at = datetime.datetime.now()
            
            return {
                "success": True,
                "message": "Trade preparation successful",
                "validated": True,
                "balances": balances,
                "task_id": task.task_id
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in trade preparation: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}
    
    async def _handle_monitor_smart_trading(self, task: AgentTask) -> Dict[str, Any]:
        """
        Monitor active smart trades and adjust parameters as needed.
        
        Args:
            task: Smart trading monitoring task
            
        Returns:
            Monitoring result dictionary
        """
        # Mark task as in-progress
        task.status = "in_progress"
        task.started_at = datetime.datetime.now()
        
        try:
            # Call service selector to monitor smart trades
            result = await self.service_selector.monitor_smart_trading(task.content)
            
            # Update task status
            task.status = "completed" if result.get("success", False) else "failed"
            task.completed_at = datetime.datetime.now()
            
            if not result.get("success", False):
                task.error = result.get("error", "Unknown error in smart trading monitoring")
                
            return {**result, "task_id": task.task_id}
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in smart trading monitoring: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}
            
    async def _handle_execute_leverage_trade(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle leverage trade execution with Mango V3.
        
        Args:
            task: Leverage trade task
            
        Returns:
            Trade execution result dictionary
        """
        # Mark task as in-progress
        task.status = "in_progress"
        task.started_at = datetime.datetime.now()
        
        # Validate required parameters
        required_params = ["market", "side", "size", "leverage"]
        missing_params = [param for param in required_params if not task.content.get(param)]
        
        if missing_params:
            error_msg = f"Missing required leverage trade parameters: {', '.join(missing_params)}"
            self.logger.error(f"Leverage trade validation failed: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}
        
        try:
            # Extract leverage trade parameters
            market = task.content.get("market", "")
            side = task.content.get("side", "")
            size = float(task.content.get("size", 0))
            leverage = float(task.content.get("leverage", 1.0))
            user_id = task.content.get("user_id")
            price = float(task.content.get("price", 0))  # 0 for market orders
            order_type = task.content.get("type", "market").lower()
            reduce_only = task.content.get("reduce_only", False)
            client_id = task.content.get("client_id", task.task_id)
            
            # Log the leverage trade attempt
            self.logger.info(
                f"Leverage trade execution: {side} {size} {market} with {leverage}x leverage"
            )
            
            # Ensure leverage manager exists (Flash-backed)
            if self.leverage_manager is None:
                try:
                    from src.leverage_trading_handler import LeverageTradeManager as _LTM
                    self.logger.info("Instantiating LeverageTradeManager for Flash leverage execution")
                    self.leverage_manager = _LTM(
                        gmgn_service=getattr(self, 'gmgn_service', None),
                        memory_system=self.memory_system,
                        logger=self.logger,
                        **self.config.get('leverage_trading', {}) if hasattr(self.config, 'get') else {}
                    )
                except Exception as ie:
                    self.logger.error(f"Failed to instantiate LeverageTradeManager: {ie}", exc_info=True)
                    raise

            # Use leverage manager (Flash) for execution
            result = await self.leverage_manager.execute_leverage_trade(
                user_id=user_id,
                market=market,
                side=side,
                size=size,
                leverage=leverage,
                order_type=order_type,
                price=price,
                reduce_only=reduce_only,
                client_id=client_id
            )
            
            # Update task status based on result
            if result.get("success", False):
                self.logger.info(f"Leverage trade executed successfully: {task.task_id}")
                task.status = "completed"
                task.result = result
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.warning(f"Leverage trade failed: {error_msg}")
                task.status = "failed"
                task.error = error_msg
            
            # Set completion timestamp
            task.completed_at = datetime.datetime.now()
            
            # Add task_id to result
            if isinstance(result, dict):
                result["task_id"] = task.task_id
            else:
                result = {"success": True, "result": result, "task_id": task.task_id}
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in leverage trade execution: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}
    
    async def _handle_modify_leverage_position(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle modification of an existing leverage position (take profit, stop loss, etc).
        
        Args:
            task: Position modification task
            
        Returns:
            Position modification result
        """
        # Mark task as in-progress
        task.status = "in_progress"
        task.started_at = datetime.datetime.now()
        
        # Validate required parameters
        required_params = ["position_id", "modification_type"]
        missing_params = [param for param in required_params if not task.content.get(param)]
        
        if missing_params:
            error_msg = f"Missing required position modification parameters: {', '.join(missing_params)}"
            self.logger.error(f"Position modification validation failed: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}
        
        try:
            # Extract modification parameters
            position_id = task.content.get("position_id")
            modification_type = task.content.get("modification_type")  # "tp", "sl", "size", "leverage"
            user_id = task.content.get("user_id")
            new_value = task.content.get("new_value")
            
            self.logger.info(
                f"Modifying position {position_id}: {modification_type} to {new_value}"
            )
            
            # Check if we have a leverage manager
            if self.leverage_manager is not None:
                # Use the leverage trade manager for modification
                result = await self.leverage_manager.modify_leverage_position(
                    user_id=user_id,
                    position_id=position_id,
                    modification_type=modification_type,
                    new_value=new_value
                )
            else:
                # Fall back to direct service selector call
                result = await self.service_selector.modify_leverage_position(
                    position_id=position_id,
                    modification_type=modification_type,
                    new_value=new_value,
                    user_id=user_id
                )
            
            # Update task status based on result
            if result.get("success", False):
                self.logger.info(f"Position modification successful: {task.task_id}")
                task.status = "completed"
                task.result = result
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.warning(f"Position modification failed: {error_msg}")
                task.status = "failed"
                task.error = error_msg
            
            # Set completion timestamp
            task.completed_at = datetime.datetime.now()
            
            # Add task_id to result
            if isinstance(result, dict):
                result["task_id"] = task.task_id
            else:
                result = {"success": True, "result": result, "task_id": task.task_id}
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in position modification: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}

    async def _get_internal_wallet_balance(self, user_id: str) -> Dict[str, float]:
        """
        Get balance from internal wallet system.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of token balances
        """
        if not user_id:
            return {}
            
        try:
            # Get wallet manager from GraceCore (centralized instance)
            from src.api_server import grace_instance
            
            # Initialize wallet manager reference
            wallet_manager = None
            
            # First try to get the internal wallet manager from GraceCore
            if grace_instance and hasattr(grace_instance, "internal_wallet_manager"):
                wallet_manager = grace_instance.internal_wallet_manager
                self.logger.info("Using centralized wallet manager from GraceCore")
            else:
                # Fall back to api_server if available
                try:
                    from src.api_server import wallet_manager as api_wallet_manager
                    wallet_manager = api_wallet_manager
                    self.logger.info("Using wallet manager from api_server")
                except ImportError:
                    self.logger.warning("No centralized wallet manager available, creating temporary instance")
                    # Create a temporary instance as last resort
                    from src.wallet_connection import InternalWalletManager
                    wallet_manager = InternalWalletManager(
                        secure_data_manager=self.config.get("secure_data_manager") if hasattr(self, "config") else None,
                        solana_rpc_url="https://api.mainnet-beta.solana.com",
                        data_dir=os.path.join(os.getcwd(), "data")
                    )
                    self.logger.warning("Created temporary wallet manager - consider using GraceCore instance for reliability")
            
            # Get wallet balance using the wallet manager
            if wallet_manager:
                # Get the user's wallet data
                user_wallet = await wallet_manager.get_user_wallet(user_id)
                
                if not user_wallet:
                    self.logger.warning(f"No wallet found for user {user_id}")
                    return {}
                    
                # Extract balance information
                balances = user_wallet.get("balance", {})
                return balances
            else:
                self.logger.warning("Cannot get internal balances: No wallet manager available")
                return {}
                
        except ImportError:
            self.logger.warning("Cannot get internal balances: Wallet connection module not available")
            return {}
        except Exception as e:
            self.logger.error(f"Error getting internal wallet balance: {str(e)}")
            return {}
            
    async def _transfer_from_internal_to_mango(self, user_id: str, token: str, amount: float) -> bool:
        """
        Transfer funds from internal wallet to Mango V3 wallet for trading.
        This ensures users can trade with funds they see in their internal wallet.
        
        Args:
            user_id: User identifier
            token: Token to transfer
            amount: Amount to transfer
            
        Returns:
            Success status
        """
        if not user_id or not token or amount <= 0:
            return False
            
        try:
            # Step 1: Get the centralized wallet manager from GraceCore
            from src.api_server import grace_instance
            
            # Initialize wallet manager reference
            wallet_manager = None
            
            # First try to get the internal wallet manager from GraceCore
            if grace_instance and hasattr(grace_instance, "internal_wallet_manager"):
                wallet_manager = grace_instance.internal_wallet_manager
                self.logger.info("Using centralized wallet manager from GraceCore for fund transfer")
            else:
                # Fall back to api_server if available
                try:
                    from src.api_server import wallet_manager as api_wallet_manager
                    wallet_manager = api_wallet_manager
                    self.logger.info("Using wallet manager from api_server for fund transfer")
                except ImportError:
                    self.logger.warning("No centralized wallet manager available, creating temporary instance")
                    # Create a temporary instance as last resort
                    from src.wallet_connection import InternalWalletManager
                    wallet_manager = InternalWalletManager(
                        secure_data_manager=self.config.get("secure_data_manager") if hasattr(self, "config") else None,
                        solana_rpc_url="https://api.mainnet-beta.solana.com",
                        data_dir=os.path.join(os.getcwd(), "data")
                    )
                    self.logger.warning("Created temporary wallet manager for fund transfer")
                except Exception as e:
                    self.logger.error(f"Failed to create wallet manager: {str(e)}")
                    return False
            
            if not wallet_manager:
                self.logger.error("Cannot transfer funds: No wallet manager available")
                return False
                
            # Deduct from internal wallet
            internal_update = await wallet_manager.update_wallet_balance(
                user_id=user_id,
                token=token.lower(),
                amount=amount,
                operation="subtract"
            )
            
            if not internal_update:
                self.logger.error(f"Failed to deduct {amount} {token} from internal wallet")
                return False
                
            # Step 2: Add to Mango V3 wallet
            # This will depend on your Mango V3 implementation - most likely a deposit function
            deposit_result = await self._deposit_to_mango_wallet(user_id, token, amount)
            
            if not deposit_result:
                # If deposit fails, revert the internal wallet deduction
                await wallet_manager.update_wallet_balance(
                    user_id=user_id,
                    token=token.lower(),
                    amount=amount,
                    operation="add"
                )
                self.logger.error(f"Failed to deposit to Mango V3 wallet, reverted internal deduction")
                return False
                
            self.logger.info(f"Successfully transferred {amount} {token} from internal to Mango V3 wallet")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in fund transfer: {str(e)}")
            return False
            
    async def _deposit_to_mango_wallet(self, user_id: str, token: str, amount: float) -> bool:
        """
        Deposit funds to Mango V3 wallet.
        
        Args:
            user_id: User identifier
            token: Token to deposit
            amount: Amount to deposit
            
        Returns:
            Success status
        """
        try:
            # Get Mango V3 service from selector
            mango_service = self.service_selector.get_service(self.service_selector.primary_service)
            
            if not mango_service:
                self.logger.error("Cannot deposit: Mango V3 service not available")
                return False
                
            # Check if deposit method exists
            if hasattr(mango_service, "deposit_funds"):
                result = await mango_service.deposit_funds(
                    user_id=user_id,
                    token=token,
                    amount=amount
                )
                return result.get("success", False)
            else:
                # If no deposit method, we'll use an accounting approach
                # Simply mark the funds as available in Mango V3's internal accounting
                # This is a simplification - in a real system, you'd need to handle actual deposits
                self.logger.info(f"Using virtual deposit for {amount} {token} (Mango V3 deposit API not available)")
                return True
                
        except Exception as e:
            self.logger.error(f"Error depositing to Mango V3: {str(e)}")
            return False
    
    async def _sync_balances_to_internal_wallet(self, user_id: str, trade_result: Dict[str, Any]) -> None:
        """
        Synchronize balances from Mango V3 to internal wallet system after a trade.
        This ensures users can see their funds in the UI they're familiar with.
        
        Args:
            user_id: User identifier
            trade_result: Result of trade execution
        """
        if not user_id:
            self.logger.warning("Cannot sync balances: No user_id provided")
            return
            
        try:
            # Extract traded token and amount from result
            market = trade_result.get("market", "")
            side = trade_result.get("side", "")
            size = float(trade_result.get("size", 0))
            
            # Handle different price field names from various services
            executed_price = 0
            price_candidates = [
                trade_result.get("executed_price"),
                trade_result.get("price"),
                trade_result.get("avg_price"),
                trade_result.get("fill_price"),
                # Check nested structures
                trade_result.get("order_details", {}).get("price"),
                trade_result.get("order", {}).get("price"),
                trade_result.get("confirmation_details", {}).get("price")
            ]
            
            # Use the first non-None value
            for price in price_candidates:
                if price is not None:
                    try:
                        executed_price = float(price)
                        if executed_price > 0:
                            break
                    except (ValueError, TypeError):
                        continue
                        
            # If no price found, try to get market price
            if executed_price <= 0:
                self.logger.warning("No executed price found in trade result, will try to get market price")
                try:
                    # Get current market price if available
                    if hasattr(self.service_selector, "get_token_price") and market:
                        token = market.split("/")[0] if "/" in market else market
                        price_info = await self.service_selector.get_token_price(token)
                        if price_info and price_info.get("success") and price_info.get("price"):
                            executed_price = float(price_info.get("price"))
                            self.logger.info(f"Using current market price: {executed_price}")
                except Exception as e:
                    self.logger.error(f"Error getting market price: {str(e)}")
                    
            if executed_price <= 0:
                self.logger.warning("Cannot determine trade price, using fallback value of 1.0")
                executed_price = 1.0  # Fallback to prevent zero calculations
            
            if not market or not side or size <= 0:
                self.logger.warning("Cannot sync balances: Missing trade information")
                return
                
            # Parse market to get base and quote tokens
            if "/" in market:
                base_token, quote_token = market.split("/")
            else:
                base_token = market
                quote_token = "USDC"  # Default quote token
                
            # Determine which token balance to update based on trade side
            # For sell orders, we need to credit the quote token (usually USDC)
            # For buy orders, we need to credit the base token (the asset purchased)
            if side.lower() == "sell":
                target_token = quote_token  # Usually USDC
                # Calculate the amount received (size * price) with a small buffer for fees
                amount = size * executed_price * 0.99  # Account for 1% potential fees
                self.logger.info(f"Sell order: Adding {amount} {target_token} to internal wallet")
            else:  # Buy order
                target_token = base_token  # The purchased asset
                amount = size  # The amount purchased
                self.logger.info(f"Buy order: Adding {amount} {target_token} to internal wallet")
            
            self.logger.info(f"Synchronizing {amount} {target_token} to internal wallet for user {user_id}")
            
            # Get wallet connection system
            try:
                from src.wallet_connection import InternalWalletManager
                
                # Try to get existing wallet manager instance
                wallet_manager = None
                
                # First check if there's an instance in api_server
                try:
                    from src.api_server import wallet_manager as api_wallet_manager
                    wallet_manager = api_wallet_manager
                except ImportError:
                    # Next check grace core
                    try:
                        if hasattr(self, "config") and hasattr(self.config, "get"):
                            # Create a new instance if needed
                            wallet_manager = InternalWalletManager(
                                secure_data_manager=self.config.get("secure_data_manager"),
                                solana_rpc_url=self.config.get("solana_rpc_url", "https://api.mainnet-beta.solana.com")
                            )
                    except Exception as e:
                        self.logger.error(f"Failed to create wallet manager: {str(e)}")
                
                # Update the internal wallet balance
                if wallet_manager:
                    # Get the user's wallet data
                    user_wallet = await wallet_manager.get_user_wallet(user_id)
                    
                    if not user_wallet:
                        self.logger.warning(f"No wallet found for user {user_id}")
                        return
                    
                    # Update the balance in the internal wallet
                    await wallet_manager.update_wallet_balance(
                        user_id=user_id,
                        token=target_token.lower(),
                        amount=amount,
                        operation="add"  # Add the funds to internal wallet
                    )
                    
                    self.logger.info(f"Successfully synchronized {amount} {target_token} to internal wallet")
                else:
                    self.logger.warning("Cannot sync balances: No wallet manager available")
            
            except ImportError:
                self.logger.warning("Cannot sync balances: Wallet connection module not available")
            except Exception as e:
                self.logger.error(f"Error synchronizing balances: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error in balance synchronization: {str(e)}")
    
    async def _handle_price_check(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle price check using Mango V3 with GMGN fallback.

        Args:
            task: Price check task

        Returns:
            Price information dictionary
        """
        # Mark task as in-progress immediately
        task.status = "in_progress"
        task.started_at = datetime.datetime.now()

        try:
            market = task.content.get("market", "")
            token = task.content.get("token", "")

            # Use either market or token parameter
            symbol = market or token

            if not symbol:
                raise ValueError("Either market or token must be specified")

            self.logger.info(f"Price check for {symbol} initiated")

            # Get market data from the service selector
            result = await self.service_selector.get_market_data(symbol)

            # Update task status
            if result.get("success", False):
                self.logger.info(f"Price check successful: {symbol}")
                task.status = "completed"
                task.result = result
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.warning(f"Price check failed: {error_msg}")
                task.status = "failed"
                task.error = error_msg

            # Set completion timestamp
            task.completed_at = datetime.datetime.now()

            # Add task_id to result for better tracking
            if isinstance(result, dict):
                result["task_id"] = task.task_id
            else:
                result = {
                    "success": True,
                    "result": result,
                    "task_id": task.task_id,
                    "symbol": symbol,
                }

            return result

        except ValueError as ve:
            # Handle value errors (typically missing or invalid parameters)
            error_msg = f"Invalid parameter: {str(ve)}"
            self.logger.error(f"Price check parameter error: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in price check: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}

    async def _handle_check_wallet_balance(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle wallet balance check using Mango V3 with GMGN fallback.

        Args:
            task: Balance check task

        Returns:
            Balance information dictionary
        """
        # Mark task as in-progress immediately
        task.status = "in_progress"
        task.started_at = datetime.datetime.now()

        # Validate required parameters
        if not task.content.get("user_id"):
            error_msg = "user_id is required for wallet balance check"
            self.logger.error(f"Wallet balance check failed: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}

        try:
            user_id = task.content.get("user_id", "")
            token = task.content.get("token", "")

            self.logger.info(
                f"Checking wallet balance for user {user_id}{' for token ' + token if token else ''}"
            )

            # Get balance via service selector
            result = await self.service_selector.check_balance(user_id, token)

            # Update task status
            if result.get("success", False):
                self.logger.info(f"Wallet balance check successful for user {user_id}")
                task.status = "completed"
                task.result = result
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.warning(f"Wallet balance check failed: {error_msg}")
                task.status = "failed"
                task.error = error_msg

            # Set completion timestamp
            task.completed_at = datetime.datetime.now()

            # Add task_id to result for better tracking
            if isinstance(result, dict):
                result["task_id"] = task.task_id
            else:
                result = {
                    "success": True,
                    "result": result,
                    "task_id": task.task_id,
                    "user_id": user_id,
                }

            return result

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in balance check: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}

    def get_trading_service(self, service_type: TradingService = TradingService.MANGO):
        """Get specific trading service instance."""
        return self.service_selector.get_service(service_type)
