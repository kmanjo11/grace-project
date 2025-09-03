"""
Leverage Trading Handler for Grace Trading System

This module provides a sophisticated, non-invasive system for managing leverage trades
with advanced conditional order capabilities and user-friendly interactions.
"""

import re
import json
import time
import logging
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

# Optional Flash helper client (direct to helper microservice)
try:
    from adapters.flash.flash_helper_client import FlashHelperClient  # type: ignore
except Exception:  # pragma: no cover
    FlashHelperClient = None  # type: ignore

class LeverageTradeCondition:
    """
    Represents a conditional leverage trade with advanced risk management.
    Refactored to work with Flash protocol via backend proxy.
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
        order_type: str = "limit",  # Mango V3 order type
        client_id: Optional[str] = None,  # For order tracking
        expiry: Optional[datetime] = None,
        max_drawdown: float = 0.05,  # 5% max drawdown
        trailing_stop: bool = False,
        reduce_only: bool = False,  # For position reduction
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

        # Margin state placeholders (protocol-agnostic)
        self.initial_margin_ratio = 0.0
        self.maintenance_margin_ratio = 0.0
        self.current_margin_ratio = 0.0
        self.free_collateral = 0.0
        self.account_leverage = 0.0

        # Risk management parameters
        self.max_drawdown = max_drawdown
        self.trailing_stop = trailing_stop
        self.high_water_mark = 0.0  # For trailing stop
        self.market_price = 0.0  # Current market price
        self.liquidation_price = 0.0  # Calculated liquidation price
        self.unrealized_pnl = 0.0  # Unrealized P&L

        # Position status
        self.status = "pending"  # pending, open, closed, liquidated
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

        price_below = self.entry_condition.get("price_below")
        price_above = self.entry_condition.get("price_above")

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

        take_profit = self.exit_condition.get("take_profit")
        stop_loss = self.exit_condition.get("stop_loss")

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
            "id": self.id,
            "user_id": self.user_id,
            "market": self.market,
            "side": self.side,
            "leverage": self.leverage,
            "size": self.size,
            "entry_condition": self.entry_condition,
            "exit_condition": self.exit_condition,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }


class LeverageTradeManager:
    """
    Manages leverage trades with advanced tracking and execution capabilities.
    Refactored to use Flash protocol via backend proxy endpoints.
    """

    def __init__(
        self,
        mango_v3_client=None,  # Deprecated
        gmgn_service=None,     # GMGN service instance (provides user context)
        memory_system=None,
        max_leverage: float = 10.0,  # Default max leverage
        min_margin_ratio: float = 0.05,  # 5% minimum margin ratio
        logger: Optional[logging.Logger] = None,
        **kwargs  # For backward compatibility with config
    ):
        """
        Initialize the LeverageTradeManager.

        Args:
            mango_v3_client: MangoV3Extension instance (deprecated, use gmgn_service)
            gmgn_service: GMGN service instance (preferred)
            memory_system: Memory system for storing trade conditions
            max_leverage: Maximum allowed leverage (default: 10.0)
            min_margin_ratio: Minimum margin ratio (default: 0.05)
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.memory_system = memory_system
        self.max_leverage = max_leverage
        self.min_margin_ratio = min_margin_ratio
        
        # Prefer gmgn_service for user context; Mango client deprecated
        self.gmgn_service = gmgn_service
        
        # Initialize trade conditions storage
        self.trade_conditions: Dict[str, List[LeverageTradeCondition]] = {}
        self.active_trades: Dict[str, Dict] = {}
        
        # Apply any additional configuration from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key) and not key.startswith('_'):
                setattr(self, key, value)
            else:
                self.logger.warning(f"Invalid config key for LeverageTradeManager: {key}")
        # In-memory trade and risk tracking
        self.memory_system = memory_system
        self.max_leverage = max_leverage
        self.min_margin_ratio = min_margin_ratio
        self.logger = logger or logging.getLogger(__name__)
        self.active_trades: Dict[str, Dict[str, LeverageTradeCondition]] = {}
        self.position_risk: Dict[str, Dict[str, float]] = {}
        self.active_limit_orders: Dict[str, Dict[str, Any]] = {}

        # Flash proxy base
        self.api_base = os.environ.get("GRACE_API_BASE", "http://localhost:9000")

        # HTTP session
        self._http = requests

        # Initialize optional direct Flash helper client when enabled
        # Enable with env FLASH_USE_CLIENT=1 or FLASH_DIRECT=1
        use_client = str(os.environ.get("FLASH_USE_CLIENT") or os.environ.get("FLASH_DIRECT") or "").strip().lower() in ("1", "true", "yes")
        self._flash_client = None
        if use_client and FlashHelperClient is not None:
            try:
                self._flash_client = FlashHelperClient()
                self.logger.info("FlashHelperClient enabled for direct helper calls")
            except Exception as e:  # pragma: no cover
                self.logger.warning(f"Failed to init FlashHelperClient, will use proxy: {e}")

    def place_limit_order(
        self,
        market: str,
        side: str,
        price: float,
        size: float,
        leverage: float = 1.0,
        reduce_only: bool = False,
        client_id: Optional[str] = None,
        user_id: Optional[str] = None,  # Optional for tracking
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
            if leverage > self.max_leverage:
                return {"success": False, "error": f"Leverage {leverage}x exceeds max {self.max_leverage}x"}

            generated_client_id = client_id or f"grace-limit-{int(time.time())}"

            # Flash adapter currently builds market orders; limit specifics may not be supported.
            # We'll submit as reduceOnly if requested, ignoring price.
            payload = {
                "market": market,
                "side": side,
                "size": size,
                "leverage": leverage,
                "reduceOnly": bool(reduce_only),
                "clientId": generated_client_id,
            }
            resp = self._post_flash("/api/flash/order", payload)
            if not resp.get("success"):
                return resp

            limit_order_details = {
                "market": market,
                "side": side,
                "price": price,
                "size": size,
                "leverage": leverage,
                "client_id": generated_client_id,
                "status": "pending_signature",
                "timestamp": time.time(),
            }

            if user_id:
                self.active_limit_orders.setdefault(user_id, {})[generated_client_id] = limit_order_details
                if self.memory_system:
                    try:
                        self.memory_system.create_memory(
                            title=f"Limit Order: {market} {side}",
                            content=json.dumps(limit_order_details),
                            tags=["limit_order", "leverage_trade"],
                        )
                    except Exception:
                        pass

            self.logger.info(f"Flash order built (limit semantics best-effort): {limit_order_details}")
            return {
                "success": True,
                "order_details": limit_order_details,
                "provider": "flash",
                "unsigned_tx_b64": resp.get("transaction"),
            }

        except Exception as e:
            self.logger.error(f"Error placing limit order (flash): {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def parse_trade_request(
        self, user_id: str, request: str
    ) -> Optional[LeverageTradeCondition]:
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
            "btc": "BTC-PERP",
            "bitcoin": "BTC-PERP",
            "eth": "ETH-PERP",
            "ethereum": "ETH-PERP",
            "sol": "SOL-PERP",
            "solana": "SOL-PERP",
        }

        # Determine market
        market_match = next((markets[m] for m in markets if m in request), None)
        if not market_match:
            return None

        # Determine side
        side = "long" if "long" in request else "short" if "short" in request else None
        if not side:
            return None

        # Extract leverage
        leverage_match = re.search(r"(\d+)x", request)
        leverage = float(leverage_match.group(1)) if leverage_match else 3.0

        # Entry and exit conditions
        entry_condition = {}
        exit_condition = {}

        # Price conditions
        price_below_match = re.search(
            r"when price falls (below|under) \$?(\d+(?:,\d{3})*(?:\.\d+)?)", request
        )
        price_above_match = re.search(
            r"when price rises (above|over) \$?(\d+(?:,\d{3})*(?:\.\d+)?)", request
        )

        if price_below_match:
            price = float(price_below_match.group(2).replace(",", ""))
            entry_condition["price_below"] = price

        if price_above_match:
            price = float(price_above_match.group(2).replace(",", ""))
            entry_condition["price_above"] = price

        # Take profit and stop loss
        take_profit_match = re.search(
            r"close at around \$?(\d+(?:,\d{3})*(?:\.\d+)?)", request
        )
        stop_loss_match = re.search(
            r"stop loss at \$?(\d+(?:,\d{3})*(?:\.\d+)?)", request
        )

        if take_profit_match:
            price = float(take_profit_match.group(1).replace(",", ""))
            exit_condition["take_profit"] = price

        if stop_loss_match:
            price = float(stop_loss_match.group(1).replace(",", ""))
            exit_condition["stop_loss"] = price

        # Create trade condition
        trade_condition = LeverageTradeCondition(
            user_id=user_id,
            market=market_match,
            side=side,
            leverage=leverage,
            entry_condition=entry_condition or None,
            exit_condition=exit_condition or None,
        )

        return trade_condition

    def add_trade_condition(
        self, trade_condition: LeverageTradeCondition
    ) -> Dict[str, Any]:
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
                "success": False,
                "message": f"Maximum of {self.max_positions} open positions reached",
            }

        # Add trade condition
        user_trades[trade_condition.id] = trade_condition
        self.active_trades[trade_condition.user_id] = user_trades

        # Optional: Persist to memory system
        if self.memory_system:
            try:
                self.memory_system.create_memory(
                    user_id=trade_condition.user_id,
                    memory_type="leverage_trade_condition",
                    content=json.dumps(trade_condition.to_dict()),
                    source="leverage_trade_handler",
                    tags=[
                        "trade_condition",
                        trade_condition.market,
                        trade_condition.side,
                    ],
                )
            except Exception as e:
                self.logger.warning(f"Failed to save trade condition to memory: {e}")

        return {
            "success": True,
            "trade_condition": trade_condition.to_dict(),
            "message": "Trade condition added successfully",
        }

    def _check_risk_limits(
        self, user_id: str, trade: LeverageTradeCondition, portfolio: Dict[str, Any]
    ) -> bool:
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
        equity = portfolio.get("total_equity", 0)
        margin_used = portfolio.get("margin_used", 0)
        free_collateral = portfolio.get("free_collateral", 0)
        account_leverage = portfolio.get("account_leverage", 0)

        # 1. Check leverage limits
        if trade.leverage > self.max_leverage:
            self.logger.warning(
                f"Trade leverage {trade.leverage}x exceeds max {self.max_leverage}x"
            )
            return False

        # 2. Check margin requirements
        required_initial_margin = (trade.size * trade.market_price) / trade.leverage
        if required_initial_margin > free_collateral:
            self.logger.warning(
                f"Insufficient collateral: needs {required_initial_margin}, has {free_collateral}"
            )
            return False

        # 3. Check maintenance margin
        new_margin_ratio = (margin_used + required_initial_margin) / equity
        if new_margin_ratio < self.min_margin_ratio:
            self.logger.warning(
                f"Margin ratio {new_margin_ratio} below minimum {self.min_margin_ratio}"
            )
            return False

        # 4. Check account leverage
        new_account_leverage = (
            (margin_used + required_initial_margin) * trade.leverage
        ) / equity
        if new_account_leverage > self.max_leverage:
            self.logger.warning(
                f"Account leverage {new_account_leverage}x would exceed max {self.max_leverage}x"
            )
            return False

        # 5. Check position concentration
        market_exposure = self.position_risk.get(user_id, {}).get(trade.market, 0)
        new_exposure = market_exposure + (
            trade.size * trade.market_price * trade.leverage
        )
        max_exposure = equity * 2  # Max 2x equity per market
        if new_exposure > max_exposure:
            self.logger.warning(
                f"Market exposure {new_exposure} would exceed max {max_exposure}"
            )
            return False

        # Update trade's margin parameters
        trade.initial_margin_ratio = required_initial_margin / (
            trade.size * trade.market_price
        )
        trade.maintenance_margin_ratio = self.min_margin_ratio
        trade.current_margin_ratio = new_margin_ratio
        trade.free_collateral = free_collateral - required_initial_margin
        trade.account_leverage = new_account_leverage

        return True

    def _calculate_safe_position_size(
        self, portfolio: Dict[str, Any], price: float, leverage: float
    ) -> float:
        """
        Calculate safe position size based on Mango V3's risk parameters.

        Args:
            portfolio: User's portfolio data from Mango V3
            price: Current market price
            leverage: Desired leverage

        Returns:
            Safe position size in base currency
        """
        equity = portfolio.get("total_equity", 0)
        free_collateral = portfolio.get("free_collateral", 0)

        # Consider both equity and free collateral
        max_risk_per_trade = 0.02  # 2% max risk per trade
        max_position_from_equity = (equity * max_risk_per_trade * leverage) / price
        max_position_from_collateral = (free_collateral * leverage) / price

        # Use the more conservative limit
        return min(max_position_from_equity, max_position_from_collateral)

    def execute_trades(
        self, current_market_prices: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute trades based on current market conditions (Flash-tailored).
        - Uses Flash order/close endpoints.
        - If a price map isn't provided, fetches Pyth prices via `get_flash_price()`
          for markets that look like perps (e.g., "BTC-PERP").
        
        Args:
            current_market_prices: Optional map of { market: price }. If omitted or missing
                                   a market, price will be fetched from Flash/Pyth.
        
        Returns:
            List of trade execution results
        """
        execution_results: List[Dict[str, Any]] = []
        prices = dict(current_market_prices or {})

        for user_id, user_trades in self.active_trades.items():
            positions = []  # Position risk can be integrated from Flash positions if needed

            for trade_id, trade_condition in list(user_trades.items()):
                market_name = trade_condition.market
                market_price = prices.get(market_name)
                if market_price is None:
                    # Default to Flash/Pyth price for *-PERP markets
                    if "-PERP" in (market_name or "").upper():
                        fetched = self.get_flash_price(market_name)
                        if fetched is not None:
                            market_price = fetched
                            prices[market_name] = fetched
                        else:
                            # Can't price this market; skip
                            continue
                    else:
                        # No price available and not a perp: skip
                        continue

                # Update market price in trade condition
                trade_condition.market_price = market_price

                # Check if we need to adjust existing position
                existing_position = next(
                    (
                        pos
                        for pos in positions
                        if pos["market"] == trade_condition.market
                    ),
                    None,
                )

                if existing_position:
                    # If we had position details, we could update tracking here
                    if trade_condition.status == "open" and trade_condition.is_exit_condition_met(market_price):
                        trade_result = self._flash_close(trade_condition.market, size=trade_condition.size)
                        if trade_result.get("success"):
                            trade_condition.status = "closed"
                            trade_condition.closed_at = datetime.now()

                # For new trades, check entry conditions and risk
                elif (
                    trade_condition.status == "pending"
                    and trade_condition.is_entry_condition_met(market_price)
                ):
                    # Execute trade via Flash order endpoint
                    side = 'buy' if trade_condition.side in ('long', 'buy') else 'sell'
                    trade_result = self._flash_order(
                        market=trade_condition.market,
                        side=side,
                        size=min(trade_condition.size, trade_condition.size),
                        leverage=min(trade_condition.leverage, self.max_leverage),
                        reduce_only=False,
                    )

                    if trade_result.get("success"):
                        trade_condition.status = "active"
                        trade_condition.executed_at = datetime.now()

                    execution_results.append(
                        {"trade_id": trade_id, "result": trade_result}
                    )

                # Check exit condition
                if (
                    trade_condition.status == "active"
                    and trade_condition.is_exit_condition_met(market_price)
                ):
                    # Close trade using Flash close endpoint
                    close_result = self._flash_close(trade_condition.market, size=trade_condition.size)

                    if close_result.get("success"):
                        trade_condition.status = "closed"
                        trade_condition.closed_at = datetime.now()
                        del user_trades[trade_id]

                    execution_results.append(
                        {"trade_id": trade_id, "result": close_result}
                    )

        return execution_results

    # --- Flash helpers ---
    def _post_flash(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self._http:
                return {"success": False, "error": "requests unavailable"}
            url = f"{self.api_base}{path}"
            r = self._http.post(url, json=payload, timeout=30)
            return r.json() if r.ok else {"success": False, "error": f"HTTP {r.status_code}", "details": r.text}
        except Exception as e:
            self.logger.error(f"Flash proxy POST {path} error: {e}")
            return {"success": False, "error": str(e)}

    def _flash_order(self, market: str, side: str, size: float, leverage: float = 1.0, reduce_only: bool = False, payout_token: Optional[str] = None, collateral_token: Optional[str] = None) -> Dict[str, Any]:
        # Prefer direct helper execute when available
        if getattr(self, "_flash_client", None):
            try:
                extra: Dict[str, Any] = {"reduceOnly": bool(reduce_only)}
                if payout_token:
                    extra["payoutTokenSymbol"] = payout_token
                if collateral_token:
                    extra["collateralTokenSymbol"] = collateral_token
                result = self._flash_client.execute_order(
                    market=market,
                    side=side,
                    size=size,
                    leverage=leverage,
                    extra=extra,
                )
                # Normalize response
                if isinstance(result, dict):
                    result.setdefault("provider", "flash")
                    if "transaction" in result:
                        result.setdefault("unsigned_tx_b64", result.get("transaction"))
                return result  # type: ignore[return-value]
            except Exception as e:
                self.logger.error(f"FlashHelperClient execute_order error: {e}")
                # Fall through to proxy
        payload = {
            "market": market,
            "side": side,
            "size": size,
            "leverage": leverage,
            "reduceOnly": bool(reduce_only),
        }
        if payout_token:
            payload["payoutTokenSymbol"] = payout_token
        if collateral_token:
            payload["collateralTokenSymbol"] = collateral_token
        resp = self._post_flash("/api/flash/order", payload)
        if resp.get("success"):
            # Include compatibility fields
            resp.setdefault("provider", "flash")
            if "transaction" in resp:
                resp.setdefault("unsigned_tx_b64", resp.get("transaction"))
        return resp

    def _flash_close(self, market: str, size: Optional[float] = None, payout_token: Optional[str] = None) -> Dict[str, Any]:
        # Prefer direct helper execute when available
        if getattr(self, "_flash_client", None):
            try:
                extra: Dict[str, Any] = {}
                if payout_token:
                    extra["payoutTokenSymbol"] = payout_token
                result = self._flash_client.execute_close(market=market, size=size, extra=extra)
                # Normalize response
                if isinstance(result, dict):
                    result.setdefault("provider", "flash")
                    if "transaction" in result:
                        result.setdefault("unsigned_tx_b64", result.get("transaction"))
                return result  # type: ignore[return-value]
            except Exception as e:
                self.logger.error(f"FlashHelperClient execute_close error: {e}")
                # Fall through to proxy
        payload: Dict[str, Any] = {"market": market}
        if size is not None:
            payload["size"] = size
        if payout_token:
            payload["payoutTokenSymbol"] = payout_token
        resp = self._post_flash("/api/flash/close", payload)
        if resp.get("success"):
            resp.setdefault("provider", "flash")
            if "transaction" in resp:
                resp.setdefault("unsigned_tx_b64", resp.get("transaction"))
        return resp

    def _flash_set_tpsl(self, market: str, take_profit: Optional[float] = None, stop_loss: Optional[float] = None, size: Optional[float] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"market": market}
        if take_profit is not None:
            payload["takeProfit"] = take_profit
        if stop_loss is not None:
            payload["stopLoss"] = stop_loss
        if size is not None:
            payload["size"] = size
        resp = self._post_flash("/api/flash/tpsl", payload)
        if resp.get("success"):
            resp.setdefault("provider", "flash")
            if "transaction" in resp:
                resp.setdefault("unsigned_tx_b64", resp.get("transaction"))
        return resp

    def _flash_get_liquidation_price(self, market: str) -> Dict[str, Any]:
        # Keep using proxy for now; helper GET variant requires additional params
        payload: Dict[str, Any] = {"market": market}
        resp = self._post_flash("/api/flash/liquidation-price", payload)
        # Response expected: { success, market, owner, liquidationPrice }
        return resp

    # --- Flash price helpers (Pyth via node-helper) ---
    def _get_flash(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            if not self._http:
                return {"success": False, "error": "requests unavailable"}
            url = f"{self.api_base}{path}"
            r = self._http.get(url, params=params or {}, timeout=15)
            return r.json() if r.ok else {"success": False, "error": f"HTTP {r.status_code}", "details": r.text}
        except Exception as e:
            self.logger.error(f"Flash proxy GET {path} error: {e}")
            return {"success": False, "error": str(e)}

    def flash_get_prices(self) -> Dict[str, Any]:
        """
        Fetch Pyth prices for current Flash pool tokens via backend proxy.
        Returns structure: { success, network, pool, prices: { SYMBOL: { price, emaPrice, exponent, ... } } }
        """
        # Prefer direct helper when available
        if getattr(self, "_flash_client", None):
            try:
                return self._flash_client.get_prices()  # type: ignore[return-value]
            except Exception as e:
                self.logger.error(f"FlashHelperClient get_prices error: {e}")
                # Fall through to proxy
        return self._get_flash("/api/flash/prices")

    def get_flash_price(self, market: str, use_ema: bool = False) -> Optional[float]:
        """
        Convenience to get a float price for a given market (e.g., 'BTC-PERP').
        Applies exponent scaling from Pyth response.
        """
        try:
            symbol = (market or "").split("-")[0].upper()
            data = self.flash_get_prices()
            if not data.get("success"):
                return None
            info = (data.get("prices", {}) or {}).get(symbol)
            if not info or not info.get("success"):
                return None
            val_str = (info.get("emaPrice") if use_ema else info.get("price"))
            exp = int(info.get("exponent", 0))
            if val_str is None:
                return None
            # price fields are big-integer components as strings; apply 10^exponent
            return float(val_str) * (10 ** exp)
        except Exception as e:
            self.logger.warning(f"Failed to get flash price for {market}: {e}")
            return None


# Example usage and testing
if __name__ == "__main__":
    # Simulated setup
    class MockGMGNService:
        def place_mango_v3_leverage_trade(self, **kwargs):
            print(f"Simulated trade: {kwargs}")
            return {"success": True}

    gmgn_service = MockGMGNService()
    trade_manager = LeverageTradeManager(gmgn_service)

    # Test parsing trade requests
    test_requests = [
        "Open a 5x long position on BTC when price falls under $90,000, close at around $100K",
        "Short ETH at 3x leverage when price rises above $3,000, stop loss at $2,800",
    ]

    for request in test_requests:
        trade_condition = trade_manager.parse_trade_request("test_user", request)
        if trade_condition:
            result = trade_manager.add_trade_condition(trade_condition)
            print(result)

    # Simulate market prices for trade execution
    market_prices = {"BTC-PERP": 89000, "ETH-PERP": 3100}

    execution_results = trade_manager.execute_trades(market_prices)
    print("Execution Results:", execution_results)
