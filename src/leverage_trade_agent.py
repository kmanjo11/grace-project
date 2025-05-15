"""
Leverage Trade Agent for Grace Trading System.
Wraps the LeverageTradeManager to integrate with the agent framework.
"""

import logging
from typing import Dict, Any, Optional
from queue import PriorityQueue, Queue
from datetime import datetime

from src.agent_framework import BaseAgent, AgentTask, AgentType
from src.leverage_trading_handler import LeverageTradeManager

class LeverageTradeAgent(BaseAgent):
    """Agent for leverage trading operations."""
    
    def __init__(
        self,
        agent_id: str,
        leverage_trade_manager: LeverageTradeManager,
        task_queue: Optional[PriorityQueue] = None,
        result_queue: Optional[Queue] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new LeverageTradeAgent.
        
        Args:
            agent_id: Unique identifier for the agent
            leverage_trade_manager: The LeverageTradeManager instance
            task_queue: Queue for incoming tasks
            result_queue: Queue for task results
            config: Agent configuration
        """
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.LEVERAGE_TRADING,
            task_queue=task_queue,
            result_queue=result_queue,
            config=config
        )
        
        self.leverage_trade_manager = leverage_trade_manager
        
        # Add supported task types
        self.supported_task_types.extend([
            "execute_leverage_trade",
            "get_leverage_positions",
            "update_leverage_trade",
            "get_trade_history"
        ])
    
    def get_trade_history(
        self, 
        user_id: str, 
        trade_type: Optional[str] = 'leverage',
        limit: int = 50,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Retrieve trade history for the agent
        
        Args:
            user_id: User identifier
            trade_type: Type of trades to retrieve
            limit: Maximum number of trades
            start_time: Optional start time filter
            end_time: Optional end time filter
        
        Returns:
            Trade history dictionary
        """
        try:
            # Use LeverageTradeManager's trade history method
            trade_history = self.leverage_trade_manager.get_trade_history(
                user_id=user_id,
                trade_type=trade_type,
                limit=limit,
                start_time=start_time,
                end_time=end_time
            )
            
            return {
                "success": True,
                "trades": trade_history.get('trades', []),
                "total_trades": trade_history.get('total_trades', 0)
            }
        except Exception as e:
            self.logger.error(f"Error retrieving trade history: {e}")
            return {
                "success": False,
                "error": str(e),
                "trades": [],
                "total_trades": 0
            }

    def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a task.
        
        Args:
            task: Task to process
            
        Returns:
            Dict: Task result
        """
        try:
            if task.task_type == "execute_leverage_trade":
                return self._handle_execute_leverage_trade(task)
            elif task.task_type == "get_leverage_positions":
                return self._handle_get_leverage_positions(task)
            elif task.task_type == "update_leverage_trade":
                return self._handle_update_leverage_trade(task)
            else:
                self.logger.warning(f"Unsupported task type: {task.task_type}")
                return {"error": f"Unsupported task type: {task.task_type}", "status": "error"}
        except Exception as e:
            self.logger.error(f"Error processing task {task.task_id} of type {task.task_type}: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def _handle_execute_leverage_trade(self, task: AgentTask) -> Dict[str, Any]:
        """Handle an execute_leverage_trade task."""
        trade_params = task.content
        user_id = trade_params.get("user_id")
        request = trade_params.get("request")
        
        if not user_id or not request:
            return {
                "success": False,
                "error": "Missing required parameters: user_id and request"
            }
            
        # Validate trade through LeverageTradeManager's risk checks
        portfolio = trade_params.get("portfolio", {})
        trade_condition = self.leverage_trade_manager.parse_trade_request(
            user_id=user_id,
            request=request
        )
        
        if not trade_condition:
            return {
                "success": False,
                "error": "Failed to parse trade request"
            }
            
        # Check risk limits
        if not self.leverage_trade_manager._check_risk_limits(
            user_id,
            trade_condition,
            portfolio
        ):
            return {
                "success": False,
                "error": "Trade exceeds risk limits"
            }
            
        # Execute trade through Mango V3
        return self.leverage_trade_manager.add_trade_condition(trade_condition)
    
    def _handle_get_leverage_positions(self, task: AgentTask) -> Dict[str, Any]:
        """Handle a get_leverage_positions task."""
        user_id = task.content.get("user_id")
        if not user_id:
            return {"error": "User ID required", "status": "error"}
            
        positions = self.leverage_trade_manager.get_user_positions(user_id)
        return {
            "success": True,
            "positions": positions
        }
    
    def _handle_update_leverage_trade(self, task: AgentTask) -> Dict[str, Any]:
        """Handle an update_leverage_trade task."""
        trade_id = task.content.get("trade_id")
        user_id = task.content.get("user_id")
        updates = task.content.get("updates", {})
        
        if not all([trade_id, user_id, updates]):
            return {"error": "Missing required parameters", "status": "error"}
            
        return self.leverage_trade_manager.update_trade_condition(
            user_id=user_id,
            trade_id=trade_id,
            updates=updates
        )
