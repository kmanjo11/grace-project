"""
Automation Coordinator

A thin orchestration layer that computes indicators, applies rules, enforces risk,
and optionally triggers execution via the TradingServiceSelector. Designed to be
stateless and invoked by TradingAgent handlers (e.g., automation_tick).
"""
from typing import Any, Dict, Optional, List
import time


class AutomationCoordinator:
    def __init__(self, memory_system=None, logger=None, dry_run: bool = False):
        self.memory_system = memory_system
        self.logger = logger
        self.dry_run = dry_run

    def evaluate_and_maybe_execute(
        self,
        user_id: str,
        strategy_config: Dict[str, Any],
        state: Dict[str, Any],
        adapters: Optional[Dict[str, Any]],
        service_selector: Any,
    ) -> Dict[str, Any]:
        """
        Evaluate the strategy for the given state and optionally execute.

        Returns an EvalResult-like dict.
        """
        ts = int(time.time() * 1000)
        protocol = (strategy_config.get("protocol") or "GMGN").upper()
        strategy_id = strategy_config.get("strategy_id") or "default"
        market = state.get("market") or "UNKNOWN"
        timeframe = state.get("timeframe") or "1m"

        # Risk mapping (internal, based on thin UI params)
        risk_level = (strategy_config.get("risk_level") or "medium").lower()
        max_trade_size = float(strategy_config.get("max_trade_size") or 1.0)
        universal_sl = strategy_config.get("stop_loss")  # e.g., 0.05 for 5%
        universal_tp = strategy_config.get("take_profit")  # e.g., 0.10 for 10%

        def _tiers(level: str) -> Dict[str, Any]:
            if level == "low":
                return {
                    "scale": 0.3,
                    "tp": [0.02, 0.05, 0.08],
                    "sl": [0.015, 0.03, 0.05],
                    "partials": [0.4, 0.35, 0.25],
                }
            if level == "high":
                return {
                    "scale": 0.9,
                    "tp": [0.05, 0.10, 0.20],
                    "sl": [0.03, 0.06, 0.10],
                    "partials": [0.4, 0.35, 0.25],
                }
            # medium default
            return {
                "scale": 0.6,
                "tp": [0.03, 0.07, 0.12],
                "sl": [0.02, 0.04, 0.07],
                "partials": [0.4, 0.35, 0.25],
            }

        policy = _tiers(risk_level)

        # Indicator/rule evaluation (placeholder, consider RSI/MA from state.indicators)
        indicators = state.get("indicators") or {}
        decision = {"action": "hold", "reason": "no-signal", "confidence": 0.0}

        # Simple demo logic using RSI if provided
        try:
            rsi = indicators.get("rsi")
            if isinstance(rsi, (int, float)):
                if rsi < 30:
                    decision = {"action": "buy", "reason": "rsi_oversold", "confidence": 0.65}
                elif rsi > 70:
                    decision = {"action": "sell", "reason": "rsi_overbought", "confidence": 0.65}
        except Exception:
            pass

        # Force flags override
        if state.get("force_buy"):
            decision = {"action": "buy", "reason": "force_buy", "confidence": 1.0}
        elif state.get("force_sell"):
            decision = {"action": "sell", "reason": "force_sell", "confidence": 1.0}

        execution_result: Dict[str, Any] = {"executed": False}

        # Determine position size using risk scale
        sized_amount = max_trade_size * float(policy.get("scale", 1.0))

        # Hard safety net check placeholder (requires current PnL/portfolio context).
        # In a full implementation, we'd compute portfolio return vs entry to apply universal SL/TP.
        # Here we just surface configured nets for transparency in the result.

        if decision["action"] in ("buy", "sell") and not self.dry_run:
            side = decision["action"]
            try:
                # TradingServiceSelector handles async internally; TradingAgent bridges.
                execution_result = {
                    "routed": True,
                    "side": side,
                    "size": sized_amount,
                    "protocol": protocol,
                    "partials": policy.get("partials"),
                    "tp_tiers": policy.get("tp"),
                    "sl_tiers": policy.get("sl"),
                    "universal_tp": universal_tp,
                    "universal_sl": universal_sl,
                }
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Execution error: {e}", exc_info=True)
                execution_result = {"executed": False, "error": str(e)}

        result = {
            "eval_id": f"{user_id}:{strategy_id}:{ts}",
            "user_id": user_id,
            "strategy_id": strategy_id,
            "protocol": protocol,
            "market": market,
            "timeframe": timeframe,
            "ts": ts,
            "indicators": indicators,
            "decision": decision,
            "execution": execution_result,
            "risk_level": risk_level,
            "risk_policy": policy,
            "universal_tp": universal_tp,
            "universal_sl": universal_sl,
            "status": "executed" if execution_result.get("executed") else "evaluated",
        }
        return result
