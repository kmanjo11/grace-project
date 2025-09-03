import os
import threading
import time
import requests
from typing import Dict, List, Tuple, Optional

# Interval mapping (string -> seconds)
INTERVAL_SECONDS: Dict[str, int] = {
    "1S": 1,
    "1": 60,
    "5": 5 * 60,
    "15": 15 * 60,
    "60": 60 * 60,
    "240": 240 * 60,
    "720": 720 * 60,
    "1D": 24 * 60 * 60,
}

class Candle:
    __slots__ = ("ts", "open", "high", "low", "close", "volume")

    def __init__(self, ts: int, price: float):
        self.ts = ts  # bucket start time in ms
        self.open = price
        self.high = price
        self.low = price
        self.close = price
        self.volume = 0.0

    def update(self, price: float):
        if price > self.high:
            self.high = price
        if price < self.low:
            self.low = price
        self.close = price

class LeverageCandlesAggregator:
    def __init__(self, adapter_base: Optional[str] = None):
        # Prefer HL_ADAPTER_BASE to stay consistent with api_server; fallback to ADAPTER_BASE
        self.adapter_base = (
            adapter_base
            or os.environ.get("HL_ADAPTER_BASE")
            or os.environ.get("ADAPTER_BASE")
            or "http://127.0.0.1:9010"
        )
        # buffers[(symbol, interval_str)] = List[Candle]
        self.buffers: Dict[Tuple[str, str], List[Candle]] = {}
        self.max_candles_per_series = 2000
        self._symbols_to_track: set[str] = set()  # e.g., { 'SOL', 'ETH' }
        self._lock = threading.Lock()
        self._stop = False
        self._thread = threading.Thread(target=self._poll_loop, name="lev-candles-poller", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True
        try:
            self._thread.join(timeout=2)
        except Exception:
            pass

    def _poll_loop(self):
        # Poll every 1 second from adapter prices endpoint
        while not self._stop:
            try:
                self._poll_once()
            except Exception:
                pass
            time.sleep(1.0)

    def _poll_once(self):
        # Expect adapter to expose /flash/prices returning a mapping or list of current prices
        url = f"{self.adapter_base}/flash/prices"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return
            data = r.json()
            now_ms = int(time.time() * 1000)

            # accepted shapes: { symbol: { price }, ... } OR [ { symbol, price }, ... ] OR {data: ...}
            if isinstance(data, dict) and "data" in data:
                data = data["data"]

            items: List[dict]
            if isinstance(data, dict):
                items = [{"symbol": k, **(v if isinstance(v, dict) else {"price": v})} for k, v in data.items()]
            elif isinstance(data, list):
                items = data
            else:
                return

            for item in items:
                try:
                    symbol = str(item.get("symbol") or item.get("token") or item.get("name") or "").upper()
                    price = float(item.get("price") or item.get("oraclePrice") or item.get("value") or 0)
                    if not symbol or price <= 0:
                        continue
                    # If tracking set is empty, accept all; otherwise only track requested symbols
                    if self._symbols_to_track and symbol not in self._symbols_to_track:
                        continue
                    self._ingest_tick(symbol, price, now_ms)
                except Exception:
                    continue
        except Exception:
            return

    def _ingest_tick(self, symbol: str, price: float, ts_ms: int):
        with self._lock:
            for interval_str, secs in INTERVAL_SECONDS.items():
                bucket_ms = (ts_ms // (secs * 1000)) * (secs * 1000)
                key = (symbol, interval_str)
                series = self.buffers.get(key)
                if not series:
                    candle = Candle(bucket_ms, price)
                    self.buffers[key] = [candle]
                    continue
                last = series[-1]
                if last.ts == bucket_ms:
                    last.update(price)
                elif last.ts < bucket_ms:
                    # Fill gap with previous close if gap exists (optional)
                    # Append new bucket
                    series.append(Candle(bucket_ms, price))
                    if len(series) > self.max_candles_per_series:
                        del series[: len(series) - self.max_candles_per_series]

    def ensure_symbol(self, market: str):
        # Expect markets like SOL-PERP; we track base symbol
        base = (market or "").split("-")[0].upper().strip()
        if not base:
            return
        with self._lock:
            self._symbols_to_track.add(base)

    def get_candles(self, market: str, interval: str, ts_from_ms: Optional[int] = None, ts_to_ms: Optional[int] = None) -> List[dict]:
        base = (market or "").split("-")[0].upper().strip()
        if not base:
            return []
        interval = self._normalize_interval(interval)
        key = (base, interval)
        with self._lock:
            series = list(self.buffers.get(key, []))
        if not series:
            return []
        out: List[dict] = []
        for c in series:
            if ts_from_ms and c.ts < ts_from_ms:
                continue
            if ts_to_ms and c.ts > ts_to_ms:
                continue
            out.append({
                "ts": c.ts,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
            })
        return out

    @staticmethod
    def _normalize_interval(interval: str) -> str:
        if not interval:
            return "60"
        u = interval.upper()
        aliases = {
            "1M": "1",
            "5M": "5",
            "15M": "15",
            "1H": "60",
            "4H": "240",
            "12H": "720",
            "D": "1D",
            "1D": "1D",
            "S": "1S",
        }
        mapped = aliases.get(u, u)
        return mapped if mapped in INTERVAL_SECONDS else "60"

# Singleton instance started on import
aggregator = LeverageCandlesAggregator()
