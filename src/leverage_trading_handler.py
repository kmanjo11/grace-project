"""
Leverage Trading Handler for Grace Trading System

This module provides a sophisticated, non-invasive system for managing leverage trades
with advanced conditional order capabilities and user-friendly interactions.
"""

import re
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

class LeverageTradeCondition:
    """
    Represents a conditional leverage trade with advanced parameters.
    """
    def __init__(
        self, 
        user_id: str,
        market: str,
        side: str,
        leverage: float,
        entry_condition: Optional[Dict[str, Any]] = None,
        exit_condition: Optional[Dict[str, Any]] = None,
        size: float = 0.01,  # Default minimal trade size
        expiry: Optional[datetime] = None
    ):
        """
        Initialize a leverage trade condition.
        
        Args:
            user_id: Unique identifier for the user
            market: Trading market/symbol
            side: Trade direction ('long' or 'short')
            leverage: Leverage multiplier
            entry_condition: Conditions for entering the trade
            exit_condition: Conditions for exiting the trade
            size: Trade size in base currency
            expiry: Optional expiration for the conditional order
        """
        self.id = f"{user_id}_{market}_{int(time.time())}"
        self.user_id = user_id
        self.market = market
        self.side = side.lower()
        self.leverage = max(1, min(leverage, 100))  # Limit leverage between 1-100x
        self.entry_condition = entry_condition or {}
        self.exit_condition = exit_condition or {}
        self.size = size
        self.expiry = expiry or datetime.now() + timedelta(days=30)
        self.status = 'pending'
        self.created_at = datetime.now()
        self.executed_at = None
        self.closed_at = None
        
    def is_entry_condition_met(self, current_price: float) -> bool:
        """
        Check if entry conditions are met.
        
        Args:
            current_price: Current market price
        
        Returns:
            Boolean indicating if entry conditions are satisfied
        """
        if not self.entry_condition:
            return True
        
        price_below = self.entry_condition.get('price_below')
        price_above = self.entry_condition.get('price_above')
        
        if price_below and current_price < price_below:
            return True
        if price_above and current_price > price_above:
            return True
        
        return False
    
    def is_exit_condition_met(self, current_price: float) -> bool:
        """
        Check if exit conditions are met.
        
        Args:
            current_price: Current market price
        
        Returns:
            Boolean indicating if exit conditions are satisfied
        """
        if not self.exit_condition:
            return False
        
        take_profit = self.exit_condition.get('take_profit')
        stop_loss = self.exit_condition.get('stop_loss')
        
        if take_profit and current_price >= take_profit:
            return True
        if stop_loss and current_price <= stop_loss:
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert trade condition to dictionary for serialization.
        
        Returns:
            Dictionary representation of the trade condition
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'market': self.market,
            'side': self.side,
            'leverage': self.leverage,
            'size': self.size,
            'entry_condition': self.entry_condition,
            'exit_condition': self.exit_condition,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }

class LeverageTradeManager:
    """
    Manages leverage trades with advanced tracking and execution capabilities.
    """
    def __init__(
        self, 
        gmgn_service,
        memory_system=None,
        max_positions: int = 6,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Leverage Trade Manager.
        
        Args:
            gmgn_service: GMGN service for trade execution
            memory_system: Optional memory system for persistent storage
            max_positions: Maximum number of open positions per user
            logger: Optional logger
        """
        self.gmgn_service = gmgn_service
        self.memory_system = memory_system
        self.max_positions = max_positions
        self.logger = logger or logging.getLogger(__name__)
        
        # In-memory trade tracking
        self.active_trades: Dict[str, Dict[str, LeverageTradeCondition]] = {}
    
    def parse_trade_request(self, user_id: str, request: str) -> Optional[LeverageTradeCondition]:
        """
        Parse natural language trade request.
        
        Args:
            user_id: User identifier
            request: Natural language trade request
        
        Returns:
            Parsed LeverageTradeCondition or None
        """
        # Normalize request
        request = request.lower()
        
        # Extract market (token/cryptocurrency)
        markets = {
            'btc': 'BTC-PERP', 
            'bitcoin': 'BTC-PERP',
            'eth': 'ETH-PERP', 
            'ethereum': 'ETH-PERP',
            'sol': 'SOL-PERP', 
            'solana': 'SOL-PERP'
        }
        
        # Determine market
        market_match = next((markets[m] for m in markets if m in request), None)
        if not market_match:
            return None
        
        # Determine side
        side = 'long' if 'long' in request else 'short' if 'short' in request else None
        if not side:
            return None
        
        # Extract leverage
        leverage_match = re.search(r'(\d+)x', request)
        leverage = float(leverage_match.group(1)) if leverage_match else 3.0
        
        # Entry and exit conditions
        entry_condition = {}
        exit_condition = {}
        
        # Price conditions
        price_below_match = re.search(r'when price falls (below|under) \$?(\d+(?:,\d{3})*(?:\.\d+)?)', request)
        price_above_match = re.search(r'when price rises (above|over) \$?(\d+(?:,\d{3})*(?:\.\d+)?)', request)
        
        if price_below_match:
            price = float(price_below_match.group(2).replace(',', ''))
            entry_condition['price_below'] = price
        
        if price_above_match:
            price = float(price_above_match.group(2).replace(',', ''))
            entry_condition['price_above'] = price
        
        # Take profit and stop loss
        take_profit_match = re.search(r'close at around \$?(\d+(?:,\d{3})*(?:\.\d+)?)', request)
        stop_loss_match = re.search(r'stop loss at \$?(\d+(?:,\d{3})*(?:\.\d+)?)', request)
        
        if take_profit_match:
            price = float(take_profit_match.group(1).replace(',', ''))
            exit_condition['take_profit'] = price
        
        if stop_loss_match:
            price = float(stop_loss_match.group(1).replace(',', ''))
            exit_condition['stop_loss'] = price
        
        # Create trade condition
        trade_condition = LeverageTradeCondition(
            user_id=user_id,
            market=market_match,
            side=side,
            leverage=leverage,
            entry_condition=entry_condition or None,
            exit_condition=exit_condition or None
        )
        
        return trade_condition
    
    def add_trade_condition(self, trade_condition: LeverageTradeCondition) -> Dict[str, Any]:
        """
        Add a new trade condition for a user.
        
        Args:
            trade_condition: Leverage trade condition to add
        
        Returns:
            Result of adding the trade condition
        """
        user_trades = self.active_trades.get(trade_condition.user_id, {})
        
        # Check maximum positions
        if len(user_trades) >= self.max_positions:
            return {
                'success': False,
                'message': f'Maximum of {self.max_positions} open positions reached'
            }
        
        # Add trade condition
        user_trades[trade_condition.id] = trade_condition
        self.active_trades[trade_condition.user_id] = user_trades
        
        # Optional: Persist to memory system
        if self.memory_system:
            try:
                self.memory_system.create_memory(
                    user_id=trade_condition.user_id,
                    memory_type='leverage_trade_condition',
                    content=json.dumps(trade_condition.to_dict()),
                    source='leverage_trade_handler',
                    tags=['trade_condition', trade_condition.market, trade_condition.side]
                )
            except Exception as e:
                self.logger.warning(f"Failed to save trade condition to memory: {e}")
        
        return {
            'success': True,
            'trade_condition': trade_condition.to_dict(),
            'message': 'Trade condition added successfully'
        }
    
    def execute_trades(self, current_market_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Execute trades based on current market conditions.
        
        Args:
            current_market_prices: Current prices for different markets
        
        Returns:
            List of trade execution results
        """
        execution_results = []
        
        for user_id, user_trades in self.active_trades.items():
            for trade_id, trade_condition in list(user_trades.items()):
                market_price = current_market_prices.get(trade_condition.market)
                
                if market_price is None:
                    continue
                
                # Check entry condition
                if trade_condition.status == 'pending' and trade_condition.is_entry_condition_met(market_price):
                    # Execute trade
                    trade_result = self.gmgn_service.place_mango_v3_leverage_trade(
                        market=trade_condition.market,
                        side=trade_condition.side,
                        price=market_price,
                        size=trade_condition.size,
                        leverage=trade_condition.leverage
                    )
                    
                    if trade_result.get('success'):
                        trade_condition.status = 'active'
                        trade_condition.executed_at = datetime.now()
                    
                    execution_results.append({
                        'trade_id': trade_id,
                        'result': trade_result
                    })
                
                # Check exit condition
                if trade_condition.status == 'active' and trade_condition.is_exit_condition_met(market_price):
                    # Close trade (opposite side)
                    close_side = 'sell' if trade_condition.side == 'long' else 'buy'
                    close_result = self.gmgn_service.place_mango_v3_leverage_trade(
                        market=trade_condition.market,
                        side=close_side,
                        price=market_price,
                        size=trade_condition.size,
                        leverage=trade_condition.leverage
                    )
                    
                    if close_result.get('success'):
                        trade_condition.status = 'closed'
                        trade_condition.closed_at = datetime.now()
                        del user_trades[trade_id]
                    
                    execution_results.append({
                        'trade_id': trade_id,
                        'result': close_result
                    })
        
        return execution_results

# Example usage and testing
if __name__ == "__main__":
    # Simulated setup
    class MockGMGNService:
        def place_mango_v3_leverage_trade(self, **kwargs):
            print(f"Simulated trade: {kwargs}")
            return {'success': True}
    
    gmgn_service = MockGMGNService()
    trade_manager = LeverageTradeManager(gmgn_service)
    
    # Test parsing trade requests
    test_requests = [
        "Open a 5x long position on BTC when price falls under $90,000, close at around $100K",
        "Short ETH at 3x leverage when price rises above $3,000, stop loss at $2,800"
    ]
    
    for request in test_requests:
        trade_condition = trade_manager.parse_trade_request('test_user', request)
        if trade_condition:
            result = trade_manager.add_trade_condition(trade_condition)
            print(result)
    
    # Simulate market prices for trade execution
    market_prices = {
        'BTC-PERP': 89000,
        'ETH-PERP': 3100
    }
    
    execution_results = trade_manager.execute_trades(market_prices)
    print("Execution Results:", execution_results)
