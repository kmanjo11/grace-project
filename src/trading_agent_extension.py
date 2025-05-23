"""
Trading Agent Extension for Grace

This module extends the TradingAgent with Mango V3 as primary service
while maintaining GMGN compatibility.
"""

from typing import Dict, Any
from src.agent_framework import AgentTask, TradingAgent
from src.trading_service_selector import TradingServiceSelector, TradingService


class EnhancedTradingAgent(TradingAgent):
    """
    Enhanced Trading Agent that uses Mango V3 as primary service.
    Non-invasive extension of the original TradingAgent.
    """

    def __init__(self, *args, **kwargs):
        """Initialize enhanced trading agent."""
        super().__init__(*args, **kwargs)

        # Initialize service selector
        self.service_selector = TradingServiceSelector(
            config=self.config, memory_system=self.memory_system
        )

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
        missing_params = [param for param in required_params if not task.content.get(param)]
        
        if missing_params:
            error_msg = f"Missing required parameters: {', '.join(missing_params)}"
            self.logger.error(f"Trade validation failed: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.datetime.now()
            return {"success": False, "error": error_msg, "task_id": task.task_id}
        
        try:
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
            }

            # Log the trade attempt
            self.logger.info(
                f"Trade execution attempt: {trade_params['side']} {trade_params['size']} {trade_params['market']} "
                f"via {task.content.get('service', 'default')}"
            )

            # Execute via service selector
            result = await self.service_selector.execute_trade(
                {**trade_params, "client_id": task.task_id}
            )

            # Update task status
            if result.get("success", False):
                self.logger.info(f"Trade executed successfully: {task.task_id}")
                task.status = "completed"
                task.result = result
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
                    "symbol": symbol
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
            
            self.logger.info(f"Checking wallet balance for user {user_id}{' for token ' + token if token else ''}")
            
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
                    "user_id": user_id
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
