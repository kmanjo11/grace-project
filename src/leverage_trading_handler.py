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
    Represents a conditional leverage trade with advanced risk management.
    Integrates directly with Mango V3's margin system.
    """
    def __init__(
        self, 
        user_id: str,
        market: str,
        side: str,
        leverage: float,
        size: float = 0.01,  # Default minimal trade size
        entry_condition: Optional[Dict[str, Any]] = None,
        exit_condition: Optional[Dict[str, Any]] = None,
        order_type: str = 'limit',  # Mango V3 order type
        client_id: Optional[str] = None,  # For order tracking
        expiry: Optional[datetime] = None,
        max_drawdown: float = 0.05,  # 5% max drawdown
        trailing_stop: bool = False,
        reduce_only: bool = False  # For position reduction
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
        # Basic trade parameters
        self.id = f"{user_id}_{market}_{int(time.time())}"
        self.user_id = user_id
        self.market = market
        self.side = side.lower()
        self.size = size
        self.leverage = max(1, min(leverage, 100))  # Limit leverage between 1-100x
        self.order_type = order_type
        self.client_id = client_id or self.id
        self.reduce_only = reduce_only
        
        # Conditions and expiry
        self.entry_condition = entry_condition or {}
        self.exit_condition = exit_condition or {}
        self.expiry = expiry or datetime.now() + timedelta(days=30)
        
        # Mango V3 specific margin parameters
        self.initial_margin_ratio = 0.0  # Required initial margin
        self.maintenance_margin_ratio = 0.0  # Required maintenance margin
        self.current_margin_ratio = 0.0  # Current margin ratio
        self.free_collateral = 0.0  # Available collateral
        self.account_leverage = 0.0  # Current account leverage
        
        # Risk management parameters
        self.max_drawdown = max_drawdown
        self.trailing_stop = trailing_stop
        self.high_water_mark = 0.0  # For trailing stop
        self.market_price = 0.0  # Current market price
        self.liquidation_price = 0.0  # Calculated liquidation price
        self.unrealized_pnl = 0.0  # Unrealized P&L
        
        # Position status
        self.status = 'pending'  # pending, open, closed, liquidated
        self.created_at = datetime.now()
        self.executed_at = None
        self.closed_at = None
        self.realized_pnl = 0.0  # Realized P&L
        
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
    Direct integration with Mango V3 for proper leverage handling.
    """
    
    def __init__(
        self,
        mango_v3_client,  # MangoV3Extension instance
        memory_system=None,
        max_leverage: float = 10.0,  # Default max leverage
        min_margin_ratio: float = 0.05,  # 5% minimum margin ratio
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Leverage Trade Manager.
        
        Args:
            mango_v3_client: Mango V3 client for trade execution
            memory_system: Optional memory system for persistent storage
            max_leverage: Maximum leverage allowed per trade
            min_margin_ratio: Minimum required margin ratio
            logger: Optional logger
        """
        self.mango = mango_v3_client
        self.memory_system = memory_system
        self.max_leverage = max_leverage
        self.min_margin_ratio = min_margin_ratio
        self.logger = logger or logging.getLogger(__name__)
        
        # In-memory trade and risk tracking
        self.active_trades: Dict[str, Dict[str, LeverageTradeCondition]] = {}
        self.position_risk: Dict[str, Dict[str, float]] = {}  # Track risk per user/market
        self.active_limit_orders: Dict[str, Dict[str, Any]] = {}  # Track active limit orders
    
    def place_limit_order(
        self, 
        market: str, 
        side: str, 
        price: float, 
        size: float, 
        leverage: float = 1.0,
        reduce_only: bool = False,
        client_id: Optional[str] = None,
        user_id: Optional[str] = None  # Optional for tracking
    ) -> Dict[str, Any]:
        """
        Place a limit order for leverage trading.
        
        Args:
            market: Trading market
            side: 'buy' or 'sell'
            price: Limit order price
            size: Order size
            leverage: Leverage multiplier
            reduce_only: Whether order should only reduce existing position
            client_id: Optional unique client identifier
            user_id: Optional user identifier for tracking
        
        Returns:
            Limit order placement result
        """
        try:
            # Validate leverage
            if leverage > self.max_leverage:
                return {
                    'success': False,
                    'error': f'Leverage {leverage}x exceeds max {self.max_leverage}x'
                }
            
            # Generate client ID if not provided
            generated_client_id = client_id or f'grace-limit-{int(time.time())}'
            
            # Place limit order via Mango V3
            order_result = self.mango.place_leverage_trade(
                market=market,
                side=side,
                price=price,
                size=size,
                leverage=leverage,
                reduce_only=reduce_only,
                order_type='limit',
                client_id=generated_client_id
            )
            
            # Track limit order
            if order_result.get('success'):
                limit_order_details = {
                    'market': market,
                    'side': side,
                    'price': price,
                    'size': size,
                    'leverage': leverage,
                    'client_id': generated_client_id,
                    'status': 'active',
                    'timestamp': time.time()
                }
                
                # Optional user tracking
                if user_id:
                    if user_id not in self.active_limit_orders:
                        self.active_limit_orders[user_id] = {}
                    self.active_limit_orders[user_id][generated_client_id] = limit_order_details
                
                # Optional: Log to memory system
                if self.memory_system and user_id:
                    self.memory_system.create_memory(
                        title=f'Limit Order: {market} {side}',
                        content=json.dumps(limit_order_details),
                        tags=['limit_order', 'leverage_trade']
                    )
                
                self.logger.info(f"Limit order placed: {limit_order_details}")
                return {
                    'success': True,
                    'order_details': limit_order_details,
                    **order_result
                }
            
            return order_result
        
        except Exception as e:
            self.logger.error(f"Error placing limit order: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
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
    
    def _check_risk_limits(self, user_id: str, trade: LeverageTradeCondition, portfolio: Dict[str, Any]) -> bool:
        """
        Check if trade meets Mango V3's risk management criteria.
        Also verifies wallet connections and fund availability.
        
        Args:
            user_id: User ID
            trade: Trade condition to check
            portfolio: User's portfolio data from Mango V3
            
        Returns:
            Boolean indicating if trade meets risk criteria
        """
        Check if trade meets Mango V3's risk management criteria.
        
        Args:
            user_id: User ID
            trade: Trade condition to check
            portfolio: User's portfolio data from Mango V3
        
        Returns:
            Boolean indicating if trade meets risk criteria
        """
        equity = portfolio.get('total_equity', 0)
        margin_used = portfolio.get('margin_used', 0)
        free_collateral = portfolio.get('free_collateral', 0)
        account_leverage = portfolio.get('account_leverage', 0)
        
        # 1. Check leverage limits
        if trade.leverage > self.max_leverage:
            self.logger.warning(f"Trade leverage {trade.leverage}x exceeds max {self.max_leverage}x")
            return False
            
        # 2. Check margin requirements
        required_initial_margin = (trade.size * trade.market_price) / trade.leverage
        if required_initial_margin > free_collateral:
            self.logger.warning(f"Insufficient collateral: needs {required_initial_margin}, has {free_collateral}")
            return False
            
        # 3. Check maintenance margin
        new_margin_ratio = (margin_used + required_initial_margin) / equity
        if new_margin_ratio < self.min_margin_ratio:
            self.logger.warning(f"Margin ratio {new_margin_ratio} below minimum {self.min_margin_ratio}")
            return False
            
        # 4. Check account leverage
        new_account_leverage = ((margin_used + required_initial_margin) * trade.leverage) / equity
        if new_account_leverage > self.max_leverage:
            self.logger.warning(f"Account leverage {new_account_leverage}x would exceed max {self.max_leverage}x")
            return False
            
        # 5. Check position concentration
        market_exposure = self.position_risk.get(user_id, {}).get(trade.market, 0)
        new_exposure = market_exposure + (trade.size * trade.market_price * trade.leverage)
        max_exposure = equity * 2  # Max 2x equity per market
        if new_exposure > max_exposure:
            self.logger.warning(f"Market exposure {new_exposure} would exceed max {max_exposure}")
            return False
            
        # Update trade's margin parameters
        trade.initial_margin_ratio = required_initial_margin / (trade.size * trade.market_price)
        trade.maintenance_margin_ratio = self.min_margin_ratio
        trade.current_margin_ratio = new_margin_ratio
        trade.free_collateral = free_collateral - required_initial_margin
        trade.account_leverage = new_account_leverage
            
        return True
        
    def _calculate_safe_position_size(self, portfolio: Dict[str, Any], price: float, leverage: float) -> float:
        """
        Calculate safe position size based on Mango V3's risk parameters.
        
        Args:
            portfolio: User's portfolio data from Mango V3
            price: Current market price
            leverage: Desired leverage
            
        Returns:
            Safe position size in base currency
        """
        equity = portfolio.get('total_equity', 0)
        free_collateral = portfolio.get('free_collateral', 0)
        
        # Consider both equity and free collateral
        max_risk_per_trade = 0.02  # 2% max risk per trade
        max_position_from_equity = (equity * max_risk_per_trade * leverage) / price
        max_position_from_collateral = (free_collateral * leverage) / price
        
        # Use the more conservative limit
        return min(max_position_from_equity, max_position_from_collateral)
        
    def execute_trades(self, current_market_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Execute trades based on current market conditions with proper risk management.
        Integrates directly with Mango V3's margin system.
        
        Args:
            current_market_prices: Current prices for different markets
        
        Returns:
            List of trade execution results
        """
        execution_results = []
        
        for user_id, user_trades in self.active_trades.items():
            # Get complete portfolio data from Mango V3
            portfolio = self.mango.get_portfolio_summary(user_id)
            if not portfolio.get('success'):
                self.logger.error(f"Failed to get portfolio for user {user_id}")
                continue
                
            # Get all open positions for position adjustment
            positions = portfolio.get('positions', [])
            
            for trade_id, trade_condition in list(user_trades.items()):
                market_price = current_market_prices.get(trade_condition.market)
                if market_price is None:
                    continue
                    
                # Update market price in trade condition
                trade_condition.market_price = market_price
                
                # Check if we need to adjust existing position
                existing_position = next(
                    (pos for pos in positions if pos['market'] == trade_condition.market),
                    None
                )
                
                if existing_position:
                    # Update position tracking
                    trade_condition.current_margin_ratio = existing_position.get('margin_ratio', 0)
                    trade_condition.liquidation_price = existing_position.get('liquidation_price', 0)
                    trade_condition.unrealized_pnl = existing_position.get('unrealized_pnl', 0)
                    
                    # Check if position needs adjustment (e.g., take profit or stop loss)
                    if trade_condition.status == 'open' and trade_condition.is_exit_condition_met(market_price):
                        trade_result = self.mango.place_leverage_trade(
                            market=trade_condition.market,
                            side='sell' if trade_condition.side == 'buy' else 'buy',  # Opposite side
                            price=market_price,
                            size=trade_condition.size,
                            leverage=trade_condition.leverage,
                            reduce_only=True,  # Important: only reduce position
                            client_id=f"{trade_condition.client_id}_close"
                        )
                        if trade_result.get('success'):
                            trade_condition.status = 'closed'
                            trade_condition.closed_at = datetime.now()
                            trade_condition.realized_pnl = trade_result.get('realized_pnl', 0)
                
                # For new trades, check entry conditions and risk
                elif trade_condition.status == 'pending' and trade_condition.is_entry_condition_met(market_price):
                    # Check wallet balance and allocate if needed
                    required_margin = trade_condition.size * market_price / trade_condition.leverage
                    mango_balance = portfolio.get('total_collateral', 0)
                    
                    if mango_balance < required_margin:
                        # Try to allocate funds from internal wallet
                        allocation_result = self.mango.deposit_funds(
                            user_id=user_id,
                            amount=required_margin - mango_balance,
                            asset='USDC'  # Default collateral
                        )
                        if not allocation_result.get('success'):
                            self.logger.error(f"Failed to allocate funds for user {user_id}")
                            continue
                        
                        # Refresh portfolio after allocation
                        portfolio = self.mango.get_portfolio_summary(user_id)
                    
                    # Perform comprehensive risk checks
                    if not self._check_risk_limits(user_id, trade_condition, portfolio):
                        continue
                    
                    # Calculate safe position size based on portfolio risk
                    safe_size = self._calculate_safe_position_size(
                        portfolio,
                        market_price,
                        trade_condition.leverage
                    )
                    
                    # Execute trade through Mango V3
                    trade_result = self.mango.place_leverage_trade(
                        market=trade_condition.market,
                        side=trade_condition.side,
                        price=market_price,
                        size=min(safe_size, trade_condition.size),
                        leverage=min(trade_condition.leverage, self.max_leverage),
                        reduce_only=False,
                        order_type=trade_condition.order_type,
                        client_id=trade_condition.client_id
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
