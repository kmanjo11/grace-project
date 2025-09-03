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
        config: Optional[Dict[str, Any]] = None,
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
            config=config,
        )

        self.leverage_trade_manager = leverage_trade_manager

        # Add supported task types
        self.supported_task_types.extend(
            [
                "execute_leverage_trade",
                "get_leverage_positions",
                "update_leverage_trade",
                "get_trade_history",
            ]
        )

    def get_trade_history(
        self,
        user_id: str,
        trade_type: Optional[str] = "leverage",
        limit: int = 50,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
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
                end_time=end_time,
            )

            return {
                "success": True,
                "trades": trade_history.get("trades", []),
                "total_trades": trade_history.get("total_trades", 0),
            }
        except Exception as e:
            self.logger.error(f"Error retrieving trade history: {e}")
            return {"success": False, "error": str(e), "trades": [], "total_trades": 0}

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
                return {
                    "error": f"Unsupported task type: {task.task_type}",
                    "status": "error",
                }
        except Exception as e:
            self.logger.error(
                f"Error processing task {task.task_id} of type {task.task_type}: {str(e)}"
            )
            return {"error": str(e), "status": "error"}

    def _handle_execute_leverage_trade(self, task: AgentTask) -> Dict[str, Any]:
        """Handle an execute_leverage_trade task."""
        trade_params = task.content
        user_id = trade_params.get("user_id")
        request = trade_params.get("request")

        if not user_id or not request:
            return {
                "success": False,
                "error": "Missing required parameters: user_id and request",
            }

        # Validate trade through LeverageTradeManager's risk checks
        portfolio = trade_params.get("portfolio", {})
        trade_condition = self.leverage_trade_manager.parse_trade_request(
            user_id=user_id, request=request
        )

        if not trade_condition:
            return {"success": False, "error": "Failed to parse trade request"}

        # Check risk limits
        if not self.leverage_trade_manager._check_risk_limits(
            user_id, trade_condition, portfolio
        ):
            return {"success": False, "error": "Trade exceeds risk limits"}

        # Optional execution modes:
        # - prompt/manual: build unsigned tx and return confirmation payload for client signing
        # - immediate: return raw Flash build response (still unsigned tx) for direct UI handling
        # - default: create conditional trade to be executed by manager when conditions met
        try:
            action = (trade_params.get("action") or "open").lower()
            immediate = bool(trade_params.get("immediate", False))
            prompt = bool(trade_params.get("prompt", trade_params.get("manual", False)))

            # Prompt/manual flow: construct unsigned tx and return confirmation_required shape
            if prompt:
                if action == "close":
                    close_size = trade_params.get("size")
                    payout_token = trade_params.get("payout_token") or trade_params.get("payoutTokenSymbol")
                    resp = self.leverage_trade_manager._flash_close(
                        market=trade_condition.market,
                        size=close_size,
                        payout_token=payout_token,
                    )
                    if not isinstance(resp, dict) or not resp.get("success"):
                        return resp if isinstance(resp, dict) else {"success": False, "error": "Unexpected response"}

                    confirmation_id = f"flash_close_{trade_condition.market}_{int(datetime.now().timestamp())}"
                    return {
                        "status": "confirmation_required",
                        "provider": "flash",
                        "flow": "perp_leverage",
                        "operation": "close",
                        "confirmation_id": confirmation_id,
                        "unsigned_tx_b64": resp.get("unsigned_tx_b64") or resp.get("transaction"),
                        "details": {
                            "market": trade_condition.market,
                            "size": close_size,
                            "payoutTokenSymbol": payout_token,
                            "user_id": user_id,
                        },
                    }
                else:
                    # Open position via Flash
                    side = 'buy' if trade_condition.side in ('long', 'buy') else 'sell'
                    payout_token = trade_params.get("payout_token") or trade_params.get("payoutTokenSymbol")
                    collateral_token = trade_params.get("collateral_token") or trade_params.get("collateralTokenSymbol")
                    resp = self.leverage_trade_manager._flash_order(
                        market=trade_condition.market,
                        side=side,
                        size=trade_condition.size,
                        leverage=trade_condition.leverage,
                        reduce_only=False,
                        payout_token=payout_token,
                        collateral_token=collateral_token,
                    )
                    if not isinstance(resp, dict) or not resp.get("success"):
                        return resp if isinstance(resp, dict) else {"success": False, "error": "Unexpected response"}

                    confirmation_id = f"flash_order_{trade_condition.market}_{int(datetime.now().timestamp())}"
                    return {
                        "status": "confirmation_required",
                        "provider": "flash",
                        "flow": "perp_leverage",
                        "operation": "open",
                        "confirmation_id": confirmation_id,
                        "unsigned_tx_b64": resp.get("unsigned_tx_b64") or resp.get("transaction"),
                        "details": {
                            "market": trade_condition.market,
                            "side": side,
                            "size": trade_condition.size,
                            "leverage": trade_condition.leverage,
                            "payoutTokenSymbol": payout_token,
                            "collateralTokenSymbol": collateral_token,
                            "user_id": user_id,
                        },
                    }

            if immediate:
                if action == "close":
                    close_size = trade_params.get("size")
                    payout_token = trade_params.get("payout_token") or trade_params.get("payoutTokenSymbol")
                    resp = self.leverage_trade_manager._flash_close(
                        market=trade_condition.market,
                        size=close_size,
                        payout_token=payout_token,
                    )
                    return resp if isinstance(resp, dict) else {"success": False, "error": "Unexpected response"}
                else:
                    # Open position via Flash
                    side = 'buy' if trade_condition.side in ('long', 'buy') else 'sell'
                    payout_token = trade_params.get("payout_token") or trade_params.get("payoutTokenSymbol")
                    collateral_token = trade_params.get("collateral_token") or trade_params.get("collateralTokenSymbol")
                    resp = self.leverage_trade_manager._flash_order(
                        market=trade_condition.market,
                        side=side,
                        size=trade_condition.size,
                        leverage=trade_condition.leverage,
                        reduce_only=False,
                        payout_token=payout_token,
                        collateral_token=collateral_token,
                    )
                    return resp if isinstance(resp, dict) else {"success": False, "error": "Unexpected response"}
        except Exception as e:
            self.logger.error(f"Direct Flash execution error: {e}")
            # Fall through to conditional flow

        # Default: conditional flow managed by LeverageTradeManager (Flash-backed)
        return self.leverage_trade_manager.add_trade_condition(trade_condition)

    def _handle_get_leverage_positions(self, task: AgentTask) -> Dict[str, Any]:
        """Handle a get_leverage_positions task."""
        user_id = task.content.get("user_id")
        if not user_id:
            return {"error": "User ID required", "status": "error"}

        positions = self.leverage_trade_manager.get_user_positions(user_id)
        return {"success": True, "positions": positions}

    def _handle_update_leverage_trade(self, task: AgentTask) -> Dict[str, Any]:
        """Handle an update_leverage_trade task."""
        trade_id = task.content.get("trade_id")
        user_id = task.content.get("user_id")
        updates = task.content.get("updates", {})

        if not all([trade_id, user_id, updates]):
            return {"error": "Missing required parameters", "status": "error"}

        return self.leverage_trade_manager.update_trade_condition(
            user_id=user_id, trade_id=trade_id, updates=updates
        )
