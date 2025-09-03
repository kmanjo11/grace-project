from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests

app = FastAPI(title="Hyperliquid Adapter", version="0.1.0")


def get_base_url():
    env = os.getenv("HL_ENV", "mainnet").lower()
    if env == "testnet":
        return "https://api.hyperliquid-testnet.xyz", env
    return "https://api.hyperliquid.xyz", "mainnet"


@app.get("/health")
def health():
    base, env = get_base_url()
    return {"ok": True, "env": env, "upstream": base}


@app.get("/orderbook")
def orderbook(symbol: str, nSigFigs: int | None = None, mantissa: int | None = None):
    """
    Returns an L2 book snapshot (up to 20 levels per side) using HL Info endpoint.
    Docs: POST /info, body { type: "l2Book", coin: <symbol>, nSigFigs?, mantissa? }
    """
    base, _ = get_base_url()
    body: dict = {"type": "l2Book", "coin": symbol}
    if nSigFigs is not None:
        if nSigFigs not in (2, 3, 4, 5):
            raise HTTPException(status_code=400, detail="nSigFigs must be one of 2,3,4,5")
        body["nSigFigs"] = nSigFigs
        if nSigFigs == 5 and mantissa is not None:
            if mantissa not in (1, 2, 5):
                raise HTTPException(status_code=400, detail="mantissa must be 1,2,5 when nSigFigs=5")
            body["mantissa"] = mantissa
    try:
        r = requests.post(f"{base}/info", json=body, timeout=10)
        r.raise_for_status()
        return JSONResponse(r.json())
    except requests.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=r.text) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Placeholders to be implemented after we confirm exact schemas (service is already usable)
@app.get("/markets")
def markets(segment: str = "perps"):
    """Return allMids for perps or spot via HL info endpoint."""
    base, _ = get_base_url()
    body: dict = {"type": "allMids"}
    if segment:
        body["seg"] = segment
    try:
        r = requests.post(f"{base}/info", json=body, timeout=10)
        r.raise_for_status()
        return JSONResponse(r.json())
    except requests.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=r.text) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trades")
def trades(symbol: str, limit: int = 200):
    return JSONResponse({"ok": False, "error": "Not implemented yet", "hint": "Candles/trades endpoint will be added next"}, status_code=501)


@app.get("/candles")
def candles(symbol: str, interval: str = "1m", n: int = 100):
    """Return candleSnapshot from HL info endpoint.

    interval examples: 1m, 5m, 1h, 4h, 1d
    """
    base, _ = get_base_url()
    body: dict = {"type": "candleSnapshot", "coin": symbol, "interval": interval, "n": n}
    try:
        r = requests.post(f"{base}/info", json=body, timeout=10)
        r.raise_for_status()
        return JSONResponse(r.json())
    except requests.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=r.text) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "9010"))
    uvicorn.run(app, host="0.0.0.0", port=port)

# ------------------------
# Flash Trade forwarders
# ------------------------
FLASH_HELPER_BASE = os.getenv("FLASH_HELPER_BASE", "http://127.0.0.1:9020")


@app.get("/flash/pools")
def flash_pools():
    try:
        r = requests.get(f"{FLASH_HELPER_BASE}/pools", timeout=10)
        r.raise_for_status()
        return JSONResponse(r.json())
    except requests.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=r.text) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/flash/markets")
def flash_markets(pool: str | None = None):
    try:
        r = requests.get(f"{FLASH_HELPER_BASE}/markets", params={"pool": pool} if pool else None, timeout=10)
        r.raise_for_status()
        return JSONResponse(r.json())
    except requests.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=r.text) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/flash/positions")
def flash_positions(owner: str):
    try:
        r = requests.get(f"{FLASH_HELPER_BASE}/positions", params={"owner": owner}, timeout=10)
        r.raise_for_status()
        return JSONResponse(r.json())
    except requests.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=r.text) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flash/quote")
def flash_quote(payload: dict):
    try:
        r = requests.post(f"{FLASH_HELPER_BASE}/quote", json=payload, timeout=15)
        r.raise_for_status()
        return JSONResponse(r.json())
    except requests.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=r.text) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flash/order")
def flash_order(payload: dict):
    try:
        r = requests.post(f"{FLASH_HELPER_BASE}/order", json=payload, timeout=20)
        r.raise_for_status()
        return JSONResponse(r.json())
    except requests.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=r.text) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
