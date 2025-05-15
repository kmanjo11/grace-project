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
            config=self.config,
            memory_system=self.memory_system
        )
        
    async def _handle_execute_trade(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle trade execution using Mango V3 with GMGN fallback.
        
        Args:
            task: Trade task to process
            
        Returns:
            Trade result dictionary
        """
        try:
            # Prepare trade parameters in Mango format
            trade_params = {
                "market": task.content.get("market", ""),
                "side": task.content.get("side", "buy"),
                "type": task.content.get("type", "market"),
                "size": float(task.content.get("size", 0)),
                "price": float(task.content.get("price", 0)) if task.content.get("price") else None
            }
            
            # Execute via service selector
            result = await self.service_selector.execute_trade({
                **trade_params,
                "client_id": task.task_id
            })
            
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
                
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in trade execution: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            return {"success": False, "error": error_msg}
            
    async def _handle_price_check(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle price check using Mango V3 with GMGN fallback.
        
        Args:
            task: Price check task
            
        Returns:
            Price information dictionary
        """
        try:
            market = task.content.get("market", "")
            return await self.service_selector.get_market_data(market)
            
        except Exception as e:
            self.logger.error(f"Error in price check: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def _handle_check_wallet_balance(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle wallet balance check using Mango V3 with GMGN fallback.
        
        Args:
            task: Balance check task
            
        Returns:
            Balance information dictionary
        """
        try:
            user_id = task.content.get("user_id", "")
            token = task.content.get("token", "")
            return await self.service_selector.check_balance(user_id, token)
            
        except Exception as e:
            self.logger.error(f"Error in balance check: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def get_trading_service(self, service_type: TradingService = TradingService.MANGO):
        """Get specific trading service instance."""
        return self.service_selector.get_service(service_type)
