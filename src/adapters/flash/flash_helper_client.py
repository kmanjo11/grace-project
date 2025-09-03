"""
Flash Helper Python client

This client calls the Flash node helper service endpoints implemented under
`src/adapters/flash/node-helper/src/server.ts`.

Default base URL is taken from env FLASH_HELPER_URL (e.g. http://localhost:9020).

Typical usage:

    from adapters.flash.flash_helper_client import FlashHelperClient

    client = FlashHelperClient()  # or FlashHelperClient(base_url="http://127.0.0.1:9020")
    health = client.health()
    positions = client.get_positions(owner="<SOL_PUBKEY>")
    quote = client.get_quote(market="BTC-PERP", side="long", size=0.1, leverage=5)
    txsig = client.execute_order(market="BTC-PERP", side="long", size=0.1, leverage=5)

Notes:
- This client is thin and intentionally avoids complex schemas; backend services
  should perform additional validation as needed.
- All requests have a default timeout; override via constructor if needed.
"""
from __future__ import annotations

import os
import json
from typing import Any, Dict, Optional

import requests


DEFAULT_BASE_URL = os.environ.get("FLASH_HELPER_URL", "http://localhost:9020")
DEFAULT_TIMEOUT = float(os.environ.get("FLASH_HELPER_TIMEOUT", "20"))


class FlashHelperError(RuntimeError):
    pass


class FlashHelperClient:
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self._session = requests.Session()
        # Accept JSON by default
        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def _handle(self, resp: requests.Response) -> Any:
        ct = resp.headers.get("content-type", "")
        text = resp.text
        if not resp.ok:
            # Try parse error body
            try:
                data = resp.json()
            except Exception:
                data = {"error": text}
            raise FlashHelperError(f"{resp.status_code} {resp.reason}: {data}")
        if "application/json" in ct:
            try:
                return resp.json()
            except Exception as e:
                raise FlashHelperError(f"Failed to parse JSON: {e}; body={text[:500]}") from e
        return text

    # ----- GET endpoints -----
    def health(self) -> Dict[str, Any]:
        r = self._session.get(self._url("/health"), timeout=self.timeout)
        return self._handle(r)

    def get_pools(self) -> Any:
        r = self._session.get(self._url("/pools"), timeout=self.timeout)
        return self._handle(r)

    def get_markets(self) -> Any:
        r = self._session.get(self._url("/markets"), timeout=self.timeout)
        return self._handle(r)

    def get_prices(self) -> Any:
        r = self._session.get(self._url("/prices"), timeout=self.timeout)
        return self._handle(r)

    def get_positions(self, owner: str) -> Any:
        if not owner:
            raise ValueError("owner is required (base58 Solana pubkey)")
        r = self._session.get(self._url("/positions"), params={"owner": owner}, timeout=self.timeout)
        return self._handle(r)

    def get_liquidation_price(self, market: str, side: str, size: float, leverage: Optional[float] = None) -> Any:
        params: Dict[str, Any] = {"market": market, "side": side, "size": size}
        if leverage is not None:
            params["leverage"] = leverage
        r = self._session.get(self._url("/liquidation-price"), params=params, timeout=self.timeout)
        return self._handle(r)

    def get_quote(self, market: str, side: str, size: float, leverage: Optional[float] = None) -> Any:
        params: Dict[str, Any] = {"market": market, "side": side, "size": size}
        if leverage is not None:
            params["leverage"] = leverage
        r = self._session.get(self._url("/quote"), params=params, timeout=self.timeout)
        return self._handle(r)

    # ----- POST execute endpoints (server-side signing) -----
    def execute_order(
        self,
        market: str,
        side: str,
        size: float,
        leverage: Optional[float] = None,
        client_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "market": market,
            "side": side,
            "size": size,
        }
        if leverage is not None:
            body["leverage"] = leverage
        if client_id is not None:
            body["clientId"] = client_id
        if extra:
            body.update(extra)
        r = self._session.post(self._url("/order/execute"), data=json.dumps(body), timeout=self.timeout)
        return self._handle(r)

    def execute_close(
        self,
        market: str,
        size: Optional[float] = None,
        reduce_only: Optional[bool] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "market": market,
        }
        if size is not None:
            body["size"] = size
        if reduce_only is not None:
            body["reduceOnly"] = reduce_only
        if extra:
            body.update(extra)
        r = self._session.post(self._url("/close/execute"), data=json.dumps(body), timeout=self.timeout)
        return self._handle(r)

    # ----- Transaction building endpoints (unsigned) if needed -----
    def build_order_tx(self, market: str, side: str, size: float, leverage: Optional[float] = None, **kwargs: Any) -> Any:
        body: Dict[str, Any] = {"market": market, "side": side, "size": size}
        if leverage is not None:
            body["leverage"] = leverage
        body.update(kwargs)
        r = self._session.post(self._url("/order"), data=json.dumps(body), timeout=self.timeout)
        return self._handle(r)

    def build_close_tx(self, market: str, size: Optional[float] = None, **kwargs: Any) -> Any:
        body: Dict[str, Any] = {"market": market}
        if size is not None:
            body["size"] = size
        body.update(kwargs)
        r = self._session.post(self._url("/close"), data=json.dumps(body), timeout=self.timeout)
        return self._handle(r)


__all__ = [
    "FlashHelperClient",
    "FlashHelperError",
]
