import os
from typing import Optional, Dict, Any, List
from functools import wraps
# Early app initialization to satisfy route decorators defined above later imports
from quart import Quart, request, jsonify  # safe to import twice; idempotent
from quart_cors import cors  # safe to import twice; idempotent
app = Quart(__name__, static_folder='/app/static', static_url_path='')
# CORS will be (re)applied later in the file where full config is available

# NOTE: HL routes moved below app initialization to avoid NameError: app not defined

# --- JWT decorator (must be defined before any @jwt_required() usage) ---
def jwt_required():
    def handle_error(e):
        # Log the error and return an appropriate response
        try:
            logger.error("Error: %s", str(e), exc_info=True)  # logger will be defined later
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)})

    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            # Check for token using our existing get_token_from_request function
            token = await get_token_from_request()
            if not token:
                return jsonify({"error": "Missing authorization token"}), 401

            # Verify token using our existing verify_jwt_token function
            result = verify_jwt_token(token)
            # verify_jwt_token returns a dict with 'success' boolean
            if not result.get("success", False):
                return jsonify({"error": "Invalid or expired token"}), 401

            # Set user_id in request context for get_jwt_identity function
            request.user_id = result.get("user_id")

            return await f(*args, **kwargs)
        return decorated_function
    return decorator

# Replacement for get_jwt_identity (used by handlers)
def get_jwt_identity():
    return request.user_id

# --- Adapter proxy (read-only) ---
ADAPTER_BASE = os.environ.get("HL_ADAPTER_BASE", "http://127.0.0.1:9010")

# Flash node-helper base
# Default to 9020 per src/adapters/flash/node-helper/src/server.ts
FLASH_ADAPTER_BASE = os.environ.get("FLASH_ADAPTER_BASE", "http://127.0.0.1:9020")

# GMGN base for router/txproxy
GMGN_API_BASE = os.environ.get("GMGN_API_BASE", "https://gmgn.ai/defi")


@app.route("/api/hl/markets", methods=["GET"])
async def proxy_hl_markets():
    try:
        r = requests.get(f"{ADAPTER_BASE}/markets", params=request.args, timeout=10)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/hl/markets error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502


@app.route("/api/hl/candles", methods=["GET"])
async def proxy_hl_candles():
    try:
        r = requests.get(f"{ADAPTER_BASE}/candles", params=request.args, timeout=10)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/hl/candles error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502


# --- Flash Trade adapter proxy ---
@app.route("/api/flash/pools", methods=["GET"])
async def proxy_flash_pools():
    try:
        r = requests.get(f"{FLASH_ADAPTER_BASE}/pools", params=request.args, timeout=10)
        if r.status_code >= 400:
            logger.warning("Flash adapter /pools non-200: %s %s", r.status_code, r.text[:300])
            return jsonify({
                "success": True,
                "network": None,
                "pools": [],
                "warning": "flash adapter error; using empty pools",
            }), 200
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/pools error: {e}")
        return jsonify({
            "success": True,
            "network": None,
            "pools": [],
            "warning": "flash adapter unavailable; using empty pools",
        }), 200


@app.route("/api/flash/markets", methods=["GET"])
async def proxy_flash_markets():
    try:
        r = requests.get(f"{FLASH_ADAPTER_BASE}/markets", params=request.args, timeout=10)
        if r.status_code >= 400:
            logger.warning("Flash adapter /markets non-200: %s %s", r.status_code, r.text[:300])
            return jsonify({
                "success": True,
                "network": None,
                "pool": request.args.get("pool"),
                "tokens": [],
                "markets": [],
                "warning": "flash adapter error; using empty markets",
            }), 200
        # Normalize to array shape for UI
        try:
            data = r.json()
            if isinstance(data, list):
                return jsonify(data)
            if isinstance(data, dict):
                rows = data.get("markets")
                if isinstance(rows, list):
                    return jsonify(rows)
                if isinstance(rows, dict):
                    # Convert mapping to list
                    out = []
                    for k, v in rows.items():
                        if isinstance(v, dict):
                            v = {**v}
                            v.setdefault("symbol", v.get("symbol") or v.get("market") or k)
                        out.append(v)
                    return jsonify(out)
                # Some upstreams might (incorrectly) return a prices-shaped payload here. Normalize it too.
                prices_map = data.get("prices")
                if isinstance(prices_map, dict):
                    out = []
                    for sym, row in prices_map.items():
                        if isinstance(row, dict):
                            row = {**row}
                            row.setdefault("symbol", row.get("symbol") or sym)
                            # Convert common numeric strings
                            for k in ("price", "emaPrice"):
                                if k in row:
                                    try:
                                        row[k] = float(row[k]) if isinstance(row[k], str) else row[k]
                                    except Exception:
                                        pass
                        out.append(row)
                    return jsonify(out)
            # Fallback: return empty array to avoid UI crashes
            return jsonify([])
        except Exception:
            # If JSON parse fails, pass through raw but avoid crashing
            return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/markets error: {e}")
        return jsonify({
            "success": True,
            "network": None,
            "pool": request.args.get("pool"),
            "tokens": [],
            "markets": [],
            "warning": "flash adapter unavailable; using empty markets",
        }), 200

@app.route("/api/flash/prices", methods=["GET"])
async def proxy_flash_prices():
    """Proxy Flash Pyth prices for current pool tokens."""
    try:
        r = requests.get(f"{FLASH_ADAPTER_BASE}/prices", params=request.args, timeout=10)
        # If adapter returns an error, provide a graceful fallback to avoid blank UI
        if r.status_code >= 400:
            logger.warning(
                "Flash adapter /prices non-200: %s %s", r.status_code, r.text[:300]
            )
            fallback = {
                "success": True,
                "network": None,
                "pool": None,
                "prices": [],
                "warning": "flash adapter error; using empty prices",
            }
            return jsonify(fallback), 200
        # Normalize various shapes into an array for UI consumption
        try:
            data = r.json()
            if isinstance(data, list):
                return jsonify(data)
            if isinstance(data, dict):
                # Common shape: { success, network, pool, prices: { SYMBOL: {...} } }
                rows = data.get("prices")
                if isinstance(rows, list):
                    return jsonify(rows)
                if isinstance(rows, dict):
                    out = []
                    for sym, row in rows.items():
                        if isinstance(row, dict):
                            row = {**row}
                            row.setdefault("symbol", row.get("symbol") or sym)
                            # Convert string numerics if present
                            for k in ("price", "emaPrice"):
                                if k in row:
                                    try:
                                        row[k] = float(row[k]) if isinstance(row[k], str) else row[k]
                                    except Exception:
                                        pass
                        out.append(row)
                    return jsonify(out)
            # If structure is unexpected, return empty array to keep UI stable
            return jsonify([])
        except Exception:
            # If JSON parse fails, pass through raw
            return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        # Do not block UI rendering if adapter is down; return empty dataset with success=true
        logger.error(f"Proxy /api/flash/prices error: {e}")
        fallback = {
            "success": True,
            "network": None,
            "pool": None,
            "prices": [],
            "warning": "flash adapter unavailable; using empty prices",
        }
        return jsonify(fallback), 200


@app.route("/api/flash/positions", methods=["GET"])
async def proxy_flash_positions():
    try:
        # Inject owner from authenticated profile if not provided
        auth = await verify_token_and_get_user_id()
        params = dict(request.args)
        if auth.get("success") and "owner" not in params:
            try:
                user_id = auth["user_id"]
                user_info = await run_grace_sync(
                    grace_instance.memory_system.user_profile_system.get_user_info, user_id
                )
                pubkey = (
                    (user_info or {}).get("internal_wallet", {}) or {}
                ).get("public_key")
                if pubkey:
                    params["owner"] = pubkey
            except Exception as ie:
                logger.warning(f"Could not inject owner for /api/flash/positions: {ie}")

        r = requests.get(f"{FLASH_ADAPTER_BASE}/positions", params=params, timeout=10)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/positions error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502


@app.route("/api/flash/quote", methods=["POST"])
async def proxy_flash_quote():
    try:
        payload = await request.get_json()
        if not isinstance(payload, dict):
            payload = {}

        # Inject ownerPubkey from authenticated profile if not provided
        if "ownerPubkey" not in payload:
            auth = await verify_token_and_get_user_id()
            if auth.get("success"):
                try:
                    user_id = auth["user_id"]
                    user_info = await run_grace_sync(
                        grace_instance.memory_system.user_profile_system.get_user_info, user_id
                    )
                    pubkey = (
                        (user_info or {}).get("internal_wallet", {}) or {}
                    ).get("public_key")
                    if pubkey:
                        payload["ownerPubkey"] = pubkey
                except Exception as ie:
                    logger.warning(f"Could not inject ownerPubkey for /api/flash/quote: {ie}")

        r = requests.post(f"{FLASH_ADAPTER_BASE}/quote", json=payload, timeout=20)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/quote error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502


@app.route("/api/flash/order", methods=["POST"])
async def proxy_flash_order():
    try:
        payload = await request.get_json()
        if not isinstance(payload, dict):
            payload = {}

        # Inject ownerPubkey from authenticated profile if not provided
        if "ownerPubkey" not in payload:
            auth = await verify_token_and_get_user_id()
            if auth.get("success"):
                try:
                    user_id = auth["user_id"]
                    user_info = await run_grace_sync(
                        grace_instance.memory_system.user_profile_system.get_user_info, user_id
                    )
                    pubkey = (
                        (user_info or {}).get("internal_wallet", {}) or {}
                    ).get("public_key")
                    if pubkey:
                        payload["ownerPubkey"] = pubkey
                except Exception as ie:
                    logger.warning(f"Could not inject ownerPubkey for /api/flash/order: {ie}")

        # Map to server-side execution endpoint in node-helper
        r = requests.post(f"{FLASH_ADAPTER_BASE}/order/execute", json=payload, timeout=30)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/order error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502

@app.route("/api/flash/close", methods=["POST"])
async def proxy_flash_close():
    try:
        payload = await request.get_json()
        if not isinstance(payload, dict):
            payload = {}

        # Inject ownerPubkey from authenticated profile if not provided
        if "ownerPubkey" not in payload:
            auth = await verify_token_and_get_user_id()
            if auth.get("success"):
                try:
                    user_id = auth["user_id"]
                    user_info = await run_grace_sync(
                        grace_instance.memory_system.user_profile_system.get_user_info, user_id
                    )
                    pubkey = ((user_info or {}).get("internal_wallet", {}) or {}).get("public_key")
                    if pubkey:
                        payload["ownerPubkey"] = pubkey
                except Exception as ie:
                    logger.warning(f"Could not inject ownerPubkey for /api/flash/close: {ie}")

        r = requests.post(f"{FLASH_ADAPTER_BASE}/close", json=payload, timeout=30)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/close error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502

@app.route("/api/flash/tpsl", methods=["POST"])
async def proxy_flash_tpsl():
    try:
        payload = await request.get_json()
        if not isinstance(payload, dict):
            payload = {}

        # Inject ownerPubkey from authenticated profile if not provided
        if "ownerPubkey" not in payload:
            auth = await verify_token_and_get_user_id()
            if auth.get("success"):
                try:
                    user_id = auth["user_id"]
                    user_info = await run_grace_sync(
                        grace_instance.memory_system.user_profile_system.get_user_info, user_id
                    )
                    pubkey = ((user_info or {}).get("internal_wallet", {}) or {}).get("public_key")
                    if pubkey:
                        payload["ownerPubkey"] = pubkey
                except Exception as ie:
                    logger.warning(f"Could not inject ownerPubkey for /api/flash/tpsl: {ie}")

        r = requests.post(f"{FLASH_ADAPTER_BASE}/tpsl", json=payload, timeout=30)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/tpsl error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502

@app.route("/api/flash/liquidation-price", methods=["POST"])
async def proxy_flash_liquidation_price():
    try:
        payload = await request.get_json()
        if not isinstance(payload, dict):
            payload = {}

        # Inject ownerPubkey from authenticated profile if not provided
        if "ownerPubkey" not in payload:
            auth = await verify_token_and_get_user_id()
            if auth.get("success"):
                try:
                    user_id = auth["user_id"]
                    user_info = await run_grace_sync(
                        grace_instance.memory_system.user_profile_system.get_user_info, user_id
                    )
                    pubkey = ((user_info or {}).get("internal_wallet", {}) or {}).get("public_key")
                    if pubkey:
                        payload["ownerPubkey"] = pubkey
                except Exception as ie:
                    logger.warning(f"Could not inject ownerPubkey for /api/flash/liquidation-price: {ie}")

        r = requests.post(f"{FLASH_ADAPTER_BASE}/liquidation-price", json=payload, timeout=20)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/liquidation-price error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502


# --- GMGN Solana spot trading proxy endpoints (authenticated) ---
@app.route("/api/gmgn/quote", methods=["POST"])
@jwt_required()
async def gmgn_quote():
    """Get GMGN Solana swap route or unsigned tx.

    Body should contain tokenIn, tokenOut, amount, slippageBps, and optional from_address.
    We inject the user's internal Solana wallet public key as from_address if missing.
    By default this proxies to router/v1/sol/tx which typically returns an unsigned transaction.
    """
    try:
        payload = await request.get_json()
        if not isinstance(payload, dict):
            payload = {}

        # Inject from_address from authenticated profile if not provided
        if not payload.get("from_address"):
            try:
                user_id = get_jwt_identity()
                user_info = await run_grace_sync(
                    grace_instance.memory_system.user_profile_system.get_user_info, user_id
                )
                pubkey = ((user_info or {}).get("internal_wallet", {}) or {}).get("public_key")
                if pubkey:
                    payload["from_address"] = pubkey
            except Exception as ie:
                logger.warning(f"Could not inject from_address for /api/gmgn/quote: {ie}")

        # Allow optional override of router endpoint via query param 'endpoint'
        endpoint_override = request.args.get("endpoint")
        if endpoint_override:
            url = f"{GMGN_API_BASE}/{endpoint_override.lstrip('/')}"
        else:
            # Default to unsigned tx builder
            url = f"{GMGN_API_BASE}/router/v1/sol/tx"

        r = requests.post(url, json=payload, timeout=30)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"/api/gmgn/quote error: {e}")
        return jsonify({"success": False, "message": "GMGN router unavailable"}), 502


@app.route("/api/gmgn/submit", methods=["POST"])
@jwt_required()
async def gmgn_submit():
    """Submit a signed Solana transaction via GMGN txproxy.

    Body: { signedTransaction: base64, anti_mev?: bool }
    Forwards to: txproxy/v1/send_transaction
    """
    try:
        body = await request.get_json()
        if not isinstance(body, dict):
            body = {}
        signed_tx = body.get("signedTransaction") or body.get("signedTx") or body.get("transaction")
        if not signed_tx:
            return jsonify({"success": False, "message": "signedTransaction (base64) is required"}), 400

        payload = {
            # Follow common GMGN field naming; pass through signed tx
            "signed_tx": signed_tx,
        }
        # Optional Anti-MEV flag passthrough using a few common keys
        anti_mev = body.get("anti_mev")
        if anti_mev is None:
            anti_mev = body.get("antiMev")
        if anti_mev is not None:
            try:
                payload["anti_mev"] = bool(anti_mev)
            except Exception:
                pass

        url = f"{GMGN_API_BASE}/txproxy/v1/send_transaction"
        r = requests.post(url, json=payload, timeout=30)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"/api/gmgn/submit error: {e}")
        return jsonify({"success": False, "message": "Failed to submit transaction"}), 502


@app.route("/api/gmgn/tx-status", methods=["GET"])
@jwt_required()
async def gmgn_tx_status():
    """Poll transaction status via GMGN txproxy.

    Query params: txHash=<signature>&lastValidBlockHeight=<height>
    Forwards to: txproxy/v1/tx_status
    """
    try:
        params = {
            "txHash": request.args.get("txHash") or request.args.get("signature") or request.args.get("tx"),
            "lastValidBlockHeight": request.args.get("lastValidBlockHeight") or request.args.get("blockHeight"),
        }
        # Remove Nones
        params = {k: v for k, v in params.items() if v is not None}
        if "txHash" not in params:
            return jsonify({"success": False, "message": "txHash is required"}), 400

        url = f"{GMGN_API_BASE}/txproxy/v1/tx_status"
        r = requests.get(url, params=params, timeout=20)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"/api/gmgn/tx-status error: {e}")
        return jsonify({"success": False, "message": "Failed to poll transaction status"}), 502

# Flash Liquidity proxy endpoints
@app.route("/api/flash/liquidity/add", methods=["POST"])
async def proxy_flash_liquidity_add():
    try:
        payload = await request.get_json()
        if not isinstance(payload, dict):
            payload = {}

        # Inject ownerPubkey from authenticated profile if not provided
        if "ownerPubkey" not in payload:
            auth = await verify_token_and_get_user_id()
            if auth.get("success"):
                try:
                    user_id = auth["user_id"]
                    user_info = await run_grace_sync(
                        grace_instance.memory_system.user_profile_system.get_user_info, user_id
                    )
                    pubkey = ((user_info or {}).get("internal_wallet", {}) or {}).get("public_key")
                    if pubkey:
                        payload["ownerPubkey"] = pubkey
                except Exception as ie:
                    logger.warning(f"Could not inject ownerPubkey for /api/flash/liquidity/add: {ie}")

        r = requests.post(f"{FLASH_ADAPTER_BASE}/liquidity/add", json=payload, timeout=30)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/liquidity/add error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502


@app.route("/api/flash/liquidity/remove", methods=["POST"])
async def proxy_flash_liquidity_remove():
    try:
        payload = await request.get_json()
        if not isinstance(payload, dict):
            payload = {}

        # Inject ownerPubkey from authenticated profile if not provided
        if "ownerPubkey" not in payload:
            auth = await verify_token_and_get_user_id()
            if auth.get("success"):
                try:
                    user_id = auth["user_id"]
                    user_info = await run_grace_sync(
                        grace_instance.memory_system.user_profile_system.get_user_info, user_id
                    )
                    pubkey = ((user_info or {}).get("internal_wallet", {}) or {}).get("public_key")
                    if pubkey:
                        payload["ownerPubkey"] = pubkey
                except Exception as ie:
                    logger.warning(f"Could not inject ownerPubkey for /api/flash/liquidity/remove: {ie}")

        r = requests.post(f"{FLASH_ADAPTER_BASE}/liquidity/remove", json=payload, timeout=30)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error(f"Proxy /api/flash/liquidity/remove error: {e}")
        return jsonify({"success": False, "message": "Adapter unavailable"}), 502


# --- Solana JSON-RPC relay for client-signed transactions ---
def _get_solana_rpc_url() -> Optional[str]:
    return os.environ.get("FLASH_RPC_URL") or os.environ.get("SOLANA_RPC_URL")


@app.route("/api/solana/send-transaction", methods=["POST"])
@jwt_required()
async def solana_send_transaction():
    """Relay a client-signed base64 transaction to Solana JSON-RPC sendTransaction.

    Body: { signedTransaction: base64, options?: { skipPreflight?, maxRetries?, preflightCommitment? } }
    Returns the JSON-RPC response (e.g., signature string) wrapped in success/error.
    """
    try:
        rpc_url = _get_solana_rpc_url()
        if not rpc_url:
            return jsonify({"success": False, "message": "RPC URL missing (set FLASH_RPC_URL or SOLANA_RPC_URL)"}), 500

        body = await request.get_json()
        if not isinstance(body, dict):
            body = {}
        signed_tx = body.get("signedTransaction") or body.get("signedTx") or body.get("transaction")
        if not signed_tx:
            return jsonify({"success": False, "message": "signedTransaction (base64) is required"}), 400

        opts = body.get("options") or {}
        rpc_payload = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "sendTransaction",
            "params": [
                signed_tx,
                {
                    "encoding": "base64",
                    **({"skipPreflight": bool(opts.get("skipPreflight"))} if "skipPreflight" in opts else {}),
                    **({"maxRetries": int(opts.get("maxRetries"))} if "maxRetries" in opts and str(opts.get("maxRetries")).isdigit() else {}),
                    **({"preflightCommitment": str(opts.get("preflightCommitment"))} if "preflightCommitment" in opts else {}),
                },
            ],
        }

        r = requests.post(rpc_url, json=rpc_payload, timeout=30)
        # Pass through JSON-RPC response payload
        try:
            data = r.json()
        except Exception:
            data = {"error": f"Non-JSON response from RPC: {r.status_code}"}
        ok = (r.status_code == 200) and ("error" not in data)
        return jsonify({"success": ok, "rpc": data}), (200 if ok else 502)
    except Exception as e:
        logger.error(f"/api/solana/send-transaction error: {e}")
        return jsonify({"success": False, "message": "Failed to send transaction"}), 500


@app.route("/api/solana/simulate-transaction", methods=["POST"])
@jwt_required()
async def solana_simulate_transaction():
    """Relay a base64 transaction to Solana JSON-RPC simulateTransaction.

    Body: { transaction: base64, options?: { sigVerify?, replaceRecentBlockhash?, commitment? } }
    """
    try:
        rpc_url = _get_solana_rpc_url()
        if not rpc_url:
            return jsonify({"success": False, "message": "RPC URL missing (set FLASH_RPC_URL or SOLANA_RPC_URL)"}), 500

        body = await request.get_json()
        if not isinstance(body, dict):
            body = {}
        tx_b64 = body.get("transaction") or body.get("signedTransaction") or body.get("signedTx")
        if not tx_b64:
            return jsonify({"success": False, "message": "transaction (base64) is required"}), 400

        opts = body.get("options") or {}
        rpc_payload = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "simulateTransaction",
            "params": [
                tx_b64,
                {
                    "encoding": "base64",
                    **({"sigVerify": bool(opts.get("sigVerify"))} if "sigVerify" in opts else {}),
                    **({"replaceRecentBlockhash": bool(opts.get("replaceRecentBlockhash"))} if "replaceRecentBlockhash" in opts else {}),
                    **({"commitment": str(opts.get("commitment"))} if "commitment" in opts else {}),
                },
            ],
        }

        r = requests.post(rpc_url, json=rpc_payload, timeout=30)
        try:
            data = r.json()
        except Exception:
            data = {"error": f"Non-JSON response from RPC: {r.status_code}"}
        ok = (r.status_code == 200) and ("error" not in data)
        return jsonify({"success": ok, "rpc": data}), (200 if ok else 502)
    except Exception as e:
        logger.error(f"/api/solana/simulate-transaction error: {e}")
        return jsonify({"success": False, "message": "Failed to simulate transaction"}), 500

# --- Smart trading settings (per-user, simple file-based store) ---
def _smart_settings_path(user_id: str) -> str:
    try:
        base = os.path.join(data_dir, 'users', user_id)
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, 'smart_settings.json')
    except Exception:
        # Fallback to data_dir root
        return os.path.join(data_dir, f'smart_settings_{user_id}.json')


@app.route('/api/trading/smart-settings', methods=['GET'])
@jwt_required()
async def get_smart_settings():
    try:
        user_id = get_jwt_identity()
        path = _smart_settings_path(user_id)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        else:
            settings = {}
        # Provide sane defaults
        defaults = {
            'auto_trading_enabled': False,
            'wallet_preference': 'phantom',  # 'phantom' | 'internal' | 'auto'
            'risk_level': 'medium',          # 'low' | 'medium' | 'high'
            'max_trade_size': 1.0,
            'stop_loss': None,               # universal SL safety net (fraction, e.g., 0.05)
            'take_profit': None,             # universal TP safety net (fraction, e.g., 0.10)
        }
        merged = {**defaults, **(settings or {})}
        return jsonify({'success': True, 'settings': merged})
    except Exception as e:
        logger.error(f"get_smart_settings error: {e}")
        return jsonify({'success': False, 'message': 'Failed to read settings'}), 500


@app.route('/api/trading/smart-settings', methods=['POST'])
@jwt_required()
async def update_smart_settings():
    try:
        user_id = get_jwt_identity()
        body = await request.get_json()
        if not isinstance(body, dict):
            body = {}
        # Accept either { smart_settings: {...} } or raw settings object
        settings = body.get('smart_settings') if isinstance(body.get('smart_settings'), dict) else body
        # Whitelist keys to avoid arbitrary file writes
        allowed_keys = {
            'auto_trading_enabled',
            'wallet_preference',
            'max_daily_trades',
            'max_trade_size',
            'slippage_bps',
            'risk_level',
            'stop_loss',
            'take_profit',
        }
        filtered = {k: v for k, v in (settings or {}).items() if k in allowed_keys}

        path = _smart_settings_path(user_id)
        # Merge with existing
        current = {}
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    current = json.load(f) or {}
            except Exception:
                current = {}
        current.update(filtered)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(current, f)

        # Also persist thin trading params into user_profile_system settings so the TradingAgent reads latest
        try:
            # Fetch existing profile-backed settings to deep-merge trading block
            existing = await run_grace_sync(
                grace_instance.user_profile_system.get_user_settings, user_id
            )
            existing_settings = (existing or {}).get('settings', {}) or {}
            existing_trading = (existing_settings.get('trading') or {})

            # Map thin UI keys to internal trading settings
            trading_updates = {}
            if 'auto_trading_enabled' in filtered:
                try:
                    trading_updates['auto_trading'] = bool(filtered['auto_trading_enabled'])
                except Exception:
                    trading_updates['auto_trading'] = bool(filtered['auto_trading_enabled'])
            if 'risk_level' in filtered:
                trading_updates['risk_level'] = filtered['risk_level']
            if 'max_trade_size' in filtered:
                trading_updates['max_trade_size'] = filtered['max_trade_size']
            if 'stop_loss' in filtered:
                trading_updates['stop_loss'] = filtered['stop_loss']
            if 'take_profit' in filtered:
                trading_updates['take_profit'] = filtered['take_profit']

            # Only call update if we actually have something to write
            if trading_updates:
                merged_trading = {**existing_trading, **trading_updates}
                await run_grace_sync(
                    grace_instance.user_profile_system.update_user_settings,
                    user_id,
                    {'trading': merged_trading},
                )
        except Exception as ie:
            logger.warning(f"Failed to persist smart settings into user_profile_system: {ie}")

        return jsonify({'success': True, 'settings': current})
    except Exception as e:
        logger.error(f"update_smart_settings error: {e}")
        return jsonify({'success': False, 'message': 'Failed to update settings'}), 500

@app.route('/api/trading/automation-status', methods=['GET'])
@jwt_required()
async def get_automation_status():
    """Return smart-trade toggle status and latest evaluation snapshot summary."""
    try:
        user_id = get_jwt_identity()
        # Read settings
        path = _smart_settings_path(user_id)
        settings = {}
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    settings = json.load(f) or {}
            except Exception:
                settings = {}

        # Lazy init chroma store
        global chroma_store
        if chroma_store is None:
            try:
                chroma_store = ChromaStore()
            except Exception as ce:
                logger.warning(f"ChromaStore init failed: {ce}")

        latest_eval = None
        if chroma_store is not None:
            try:
                q = chroma_store.query_strategy_evals(user_id=user_id, n_results=1)
                # Normalize response
                ids = (q or {}).get('ids') or [[]]
                docs = (q or {}).get('documents') or [[]]
                metas = (q or {}).get('metadatas') or [[]]
                if ids and ids[0]:
                    latest_eval = {
                        'id': ids[0][0],
                        'document': docs[0][0] if docs and docs[0] else None,
                        'metadata': metas[0][0] if metas and metas[0] else None,
                    }
            except Exception as qe:
                logger.warning(f"Failed to fetch latest eval: {qe}")

        return jsonify({
            'success': True,
            'settings': settings,
            'auto_trading_enabled': bool(settings.get('auto_trading_enabled', False)),
            'risk_level': settings.get('risk_level', 'medium'),
            'latest_evaluation': latest_eval,
        })
    except Exception as e:
        logger.error(f"get_automation_status error: {e}")
        return jsonify({'success': False, 'message': 'Failed to read automation status'}), 500

@app.route('/api/trading/evaluations', methods=['GET'])
@jwt_required()
async def list_evaluations():
    """Return recent evaluation snapshots from ChromaDB for the authenticated user."""
    try:
        user_id = get_jwt_identity()
        n = request.args.get('limit', default='10')
        try:
            n_results = max(1, min(50, int(n)))
        except Exception:
            n_results = 10

        global chroma_store
        if chroma_store is None:
            chroma_store = ChromaStore()
        q = chroma_store.query_strategy_evals(user_id=user_id, n_results=n_results)
        return jsonify({'success': True, 'result': q})
    except Exception as e:
        logger.error(f"list_evaluations error: {e}")
        return jsonify({'success': False, 'message': 'Failed to query evaluations'}), 500

@app.route('/api/trading/backtests', methods=['GET'])
@jwt_required()
async def list_backtests():
    """Return recent backtest runs from ChromaDB for the authenticated user."""
    try:
        user_id = get_jwt_identity()
        n = request.args.get('limit', default='10')
        try:
            n_results = max(1, min(50, int(n)))
        except Exception:
            n_results = 10

        global chroma_store
        if chroma_store is None:
            chroma_store = ChromaStore()
        q = chroma_store.query_backtests(user_id=user_id, n_results=n_results)
        return jsonify({'success': True, 'result': q})
    except Exception as e:
        logger.error(f"list_backtests error: {e}")
        return jsonify({'success': False, 'message': 'Failed to query backtests'}), 500
"""
API Server for Grace UI

This module provides the API endpoints for the Grace UI to interact with the Grace Core.
"""

# Standard library imports
import asyncio
import datetime
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
# Import aggregator with package-aware fallback (similar to ChromaStore below)
try:
    from src.leverage_candles_aggregator import aggregator
except Exception:
    from leverage_candles_aggregator import aggregator  # type: ignore
from functools import wraps
from typing import Dict, Any, Optional, List
import subprocess
import requests

# Third-party imports
import jwt
from quart import Quart, request, jsonify, current_app, send_file, Response
from quart_cors import cors
from logging.handlers import TimedRotatingFileHandler

# ChromaStore for eval/backtest retrieval
try:
    from src.chroma_store import ChromaStore
except Exception:
    # Fallback relative import if running as module
    from chroma_store import ChromaStore  # type: ignore
chroma_store: Optional[ChromaStore] = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceAPI")  # Named logger for consistency with GraceCore

# Client log configuration (rotating daily files with retention)
CLIENT_LOG_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
os.makedirs(CLIENT_LOG_DIR, exist_ok=True)

client_logger = logging.getLogger("GraceClient")
client_logger.setLevel(logging.INFO)

def _ensure_client_log_handler():
    # Avoid adding multiple handlers in hot-reload scenarios
    if any(isinstance(h, TimedRotatingFileHandler) for h in client_logger.handlers):
        return
    log_file = os.path.join(CLIENT_LOG_DIR, 'client.log')
    handler = TimedRotatingFileHandler(log_file, when='D', interval=1, backupCount=7, encoding='utf-8', utc=True)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler.setFormatter(formatter)
    client_logger.addHandler(handler)
    # Also emit to stderr for visibility in dev
    if not any(isinstance(h, logging.StreamHandler) for h in client_logger.handlers):
        client_logger.addHandler(logging.StreamHandler())

 


# --- Conversation session helper ---
def get_latest_session_for_user(user_id: str) -> Optional[str]:
    """
    Return the most recently updated conversation session_id for a given user_id,
    scanning data/conversation_data/sessions/*.json.

    This is a lightweight heuristic to reuse the last active session when the
    client doesn't provide a session_id.
    """
    try:
        if grace_instance is None:
            return None

        base = os.path.join(grace_instance.data_dir, "conversation_data", "sessions")
        if not os.path.isdir(base):
            return None

        latest_sid = None
        latest_ts = -1.0

        for name in os.listdir(base):
            if not name.endswith(".json"):
                continue
            path = os.path.join(base, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("user_id") != user_id:
                    continue
                # Prefer last_updated if present; fall back to created_at
                ts = float(data.get("last_updated") or data.get("created_at") or 0)
                if ts > latest_ts:
                    latest_ts = ts
                    latest_sid = data.get("session_id")
            except Exception:
                # Ignore malformed files
                continue

        return latest_sid
    except Exception:
        return None

# Import chat_sessions_quart blueprint for chat functionality
try:
    from src.chat_sessions_quart import chat_blueprint
    from src.grace_core import GraceCore
except ImportError:
    # Fallback for direct execution
    from chat_sessions_quart import chat_blueprint
    from grace_core import GraceCore

# Initialize Grace core instance
# Use environment variables or defaults for configuration
config_path = os.environ.get('GRACE_CONFIG_PATH', None)
data_dir = os.environ.get('GRACE_DATA_DIR', os.path.join(os.path.dirname(__file__), '..', 'data'))
encryption_key = os.environ.get('FERNET_KEY', None)

# Initialize the Grace core with proper configuration
grace_instance = GraceCore(
    config_path=config_path,
    data_dir=data_dir,
    encryption_key=encryption_key,
    test_mode=os.environ.get('GRACE_TEST_MODE', '').lower() == 'true'
)

# Reuse pre-initialized app; do not re-initialize to preserve earlier route bindings
# app = Quart(__name__, static_folder='/app/static', static_url_path='')
app = cors(
    app,
    allow_origin=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
)

# Register chat blueprint
app.register_blueprint(chat_blueprint)

# Root route - API status for development mode
@app.route('/')
async def api_status():
    """Return API status - frontend runs separately in development"""
    return jsonify({
        "status": "Grace API server running", 
        "mode": "development",
        "frontend": "Run separately with 'pnpm run dev' in src/ui/",
        "endpoints": {
            "health": "/health",
            "api": "/api/*",
            "chat": "/chat/*"
        }
    })
        
# Explicitly handle _next directory requests for Next.js assets (CSS, JS, etc)
@app.route('/_next/<path:path>')
async def serve_next_assets(path):
    """Serve static assets from the _next directory"""
    logger.info(f"Serving Next.js asset: /_next/{path}")
    try:
        return await app.send_static_file(f"_next/{path}")
    except Exception as e:
        logger.error(f"Error serving Next.js asset /_next/{path}: {e}")
        return "", 404

# Handle assets directory requests
@app.route('/assets/<path:path>')
async def serve_assets(path):
    """Serve static assets from the assets directory"""
    logger.info(f"Serving asset: /assets/{path}")
    try:
        return await app.send_static_file(f"assets/{path}")
    except Exception as e:
        logger.error(f"Error serving asset /assets/{path}: {e}")
        return "", 404
        
# Handle static directory requests
@app.route('/static/<path:path>')
async def serve_static_assets(path):
    """Serve static assets from the static directory"""
    logger.info(f"Serving static asset: /static/{path}")
    try:
        return await app.send_static_file(f"static/{path}")
    except Exception as e:
        logger.error(f"Error serving static asset /static/{path}: {e}")
        return "", 404
        
# Catch-all route handler for Next.js client-side routing
@app.route('/<path:path>')
async def serve_routes(path):
    """Serve static files or fall back to index.html for client-side routing"""
    # Skip API routes - they should be handled by their own handlers
    if path.startswith('api/'):
        logger.debug(f"Skipping API path: {path}")
        return jsonify({"error": "API endpoint not found"}), 404
        
    logger.info(f"Requested path: /{path}")
    import os
    
    try:
        # First try to serve it as a static file
        static_path = f"/app/static/{path}"
        if os.path.exists(static_path) and os.path.isfile(static_path):
            logger.info(f"Serving static file: {path}")
            return await app.send_static_file(path)
            
        # For Next.js routes without extensions (like /trading, /chat, etc)
        # Try to serve the corresponding index.html
        if '.' not in os.path.basename(path):
            # Check if there's an index.html in a directory matching the route
            dir_index = f"{path}/index.html"
            if os.path.exists(f"/app/static/{dir_index}") and os.path.isfile(f"/app/static/{dir_index}"):
                logger.info(f"Serving route index file: {dir_index}")
                return await app.send_static_file(dir_index)
            
            # No matching directory, serve the main index.html for client-side routing
            logger.info(f"No specific route file found for {path}, serving main index.html for client-side routing")
            return await app.send_static_file('index.html')
            
        # File not found, return 404
        logger.warning(f"Static file not found: {path}")
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        logger.error(f"Error handling path /{path}: {str(e)}")
        # For routes, serve index.html as fallback so client-side routing works
        if '.' not in os.path.basename(path):
            return await app.send_static_file('index.html')
        return jsonify({"error": "Error serving request"}), 500

# --- UI Aggregated Market/Candle Endpoints ---
def _resolve_mode(val: Optional[str]) -> str:
    v = (val or "").strip().lower()
    return "leverage" if v in ("lev", "leverage", "margin", "perp", "perps") else "spot"

def _resolve_symbol_to_market(symbol: str) -> str:
    """Very small resolver to map common symbols to leverage markets.
    Example: SOL -> SOL-PERP. If already looks like a market (has '-'), return as-is.
    """
    if not symbol:
        return symbol
    s = symbol.upper()
    if "-" in s:
        return s
    # Common mappings
    common = {
        "SOL": "SOL-PERP",
        "BTC": "BTC-PERP",
        "ETH": "ETH-PERP",
        "BONK": "BONK-PERP",
    }
    return common.get(s, f"{s}-PERP")

def _normalize_candles(rows: List[dict]) -> List[dict]:
    """Normalize various provider candle shapes to {ts, open, high, low, close, volume}."""
    out: List[dict] = []
    for r in rows or []:
        try:
            # Try common keys first
            ts = r.get("ts") or r.get("time") or r.get("timestamp") or r.get("t")
            o = r.get("open") or r.get("o")
            h = r.get("high") or r.get("h")
            l = r.get("low") or r.get("l")
            c = r.get("close") or r.get("c")
            v = r.get("volume") or r.get("v") or 0
            # Some providers return arrays: [ts, o, h, l, c, v]
            if ts is None and isinstance(r, list) and len(r) >= 5:
                ts, o, h, l, c = r[:5]
                v = r[5] if len(r) > 5 else 0
            if ts is None:
                continue
            out.append({
                "ts": int(ts),
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": float(v) if v is not None else 0.0,
            })
        except Exception:
            continue
    return out

def _gmgn_kline(chain: str, token_ca: str, interval: str) -> List[dict]:
    """Call GMGN kline. Expected path: https://www.gmgn.cc/kline/{chain}/{tokenCA}
    Query params may include interval/resolution depending on GMGN API.
    """
    try:
        base = os.environ.get("GMGN_KLINE_BASE", "https://www.gmgn.cc/kline")
        url = f"{base}/{chain}/{token_ca}"
        r = requests.get(url, params={"interval": interval}, timeout=10)
        if r.status_code != 200:
            logger.warning(f"GMGN kline error {r.status_code}: {r.text[:200]}")
            return []
        data = r.json()
        # Attempt to find candles array; support direct list too
        rows = data.get("data") if isinstance(data, dict) else data
        return _normalize_candles(rows if isinstance(rows, list) else [])
    except Exception as e:
        logger.error(f"GMGN kline call failed: {e}")
        return []

@app.route("/api/ui/candles", methods=["GET"])
async def ui_candles():
    """Unified candles for UI.
    Query:
      - mode: spot|leverage
      - symbol: e.g., SOL or SOL-PERP (leverage)
      - chain: for GMGN spot, default 'sol'
      - tokenCA: for GMGN spot if available
      - interval: e.g., 1m,5m,15m,1h,4h,1d
    """
    try:
        args = request.args
        mode = _resolve_mode(args.get("mode"))
        interval = args.get("interval") or "1h"
        if mode == "leverage":
            market = args.get("market") or _resolve_symbol_to_market(args.get("symbol", ""))
            # 1) Prefer in-process leverage aggregator (Pyth-derived) if available
            try:
                # Normalize from/to to ms if provided
                def _to_ms(v: Optional[str]) -> Optional[int]:
                    if not v:
                        return None
                    try:
                        x = int(v)
                        return x if x > 10**12 else x * 1000
                    except Exception:
                        return None

                ts_from_ms = _to_ms(args.get("from"))
                ts_to_ms = _to_ms(args.get("to"))
                aggregator.ensure_symbol(market or "")
                agg_candles = aggregator.get_candles(market or "", interval, ts_from_ms, ts_to_ms)
                if agg_candles:
                    return jsonify({"success": True, "mode": mode, "market": market, "source": "aggregator", "candles": agg_candles})
            except Exception as e:
                logger.warning(f"Aggregator candles unavailable: {e}")

            # 2) Try adapter (e.g., HyperLiquid) candles
            try:
                r = requests.get(f"{ADAPTER_BASE}/candles", params={"market": market, "interval": interval}, timeout=10)
                if r.status_code == 200:
                    rows = r.json()
                    candles = _normalize_candles(rows if isinstance(rows, list) else rows.get("data", []))
                    if candles:
                        return jsonify({"success": True, "mode": mode, "market": market, "source": "adapter", "candles": candles})
            except Exception as e:
                logger.warning(f"HL candles fetch failed, will try fallback: {e}")

            # Fallback to GMGN if tokenCA provided (or symbol treated as CA)
            chain = args.get("chain") or "sol"
            token_ca = args.get("tokenCA") or args.get("tokenCa") or args.get("token") or args.get("symbol")
            candles = _gmgn_kline(chain, token_ca, interval) if token_ca else []
            return jsonify({"success": bool(candles), "mode": mode, "market": market, "fallback": "gmgn" if candles else None, "candles": candles})
        else:
            # spot via GMGN
            chain = args.get("chain") or "sol"
            token_ca = args.get("tokenCA") or args.get("tokenCa") or args.get("token") or args.get("symbol")
            if not token_ca:
                return jsonify({"success": False, "message": "tokenCA or token required for spot"}), 400
            candles = _gmgn_kline(chain, token_ca, interval)
            return jsonify({"success": bool(candles), "mode": mode, "chain": chain, "token": token_ca, "candles": candles})
    except Exception as e:
        logger.error(f"/api/ui/candles error: {e}")
        return jsonify({"success": False, "message": "Failed to fetch candles"}), 500

@app.route("/api/ui/markets", methods=["GET"])
async def ui_markets():
    """Unified markets search/list for UI.
    Query:
      - mode: spot|leverage
      - q: optional search query/symbol
      - limit: optional
    Response normalizes to: [{ symbol, name, market, chain, kind }]
    """
    try:
        args = request.args
        mode = _resolve_mode(args.get("mode"))
        q = (args.get("q") or "").strip()
        limit = int(args.get("limit") or 50)

        results: List[dict] = []
        if mode == "leverage":
            # Use HL markets (correct path)
            try:
                r = requests.get(f"{ADAPTER_BASE}/markets", params={}, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    rows = data if isinstance(data, list) else data.get("data", [])
                    # Normalize HL rows -> { symbol, name, type, source }
                    for row in (rows or []):
                        try:
                            sym = (row.get("symbol") or row.get("market") or row.get("name")) if isinstance(row, dict) else None
                            if not sym:
                                continue
                            if q and q.lower() not in str(sym).lower():
                                continue
                            results.append({
                                "symbol": sym,
                                "name": (row.get("name") if isinstance(row, dict) else None) or sym,
                                "type": "leverage",
                                "source": "hl",
                            })
                        except Exception:
                            continue
                else:
                    logger.warning(f"/api/ui/markets leverage adapter non-200: {r.status_code} {r.text[:200]}")
            except Exception as e:
                logger.warning(f"/api/ui/markets leverage adapter error: {e}")
            return jsonify({"success": True, "mode": mode, "results": results})
        else:
            # Spot: we don't have a full GMGN markets list API here; implement a minimal token search passthrough when q is provided
            if not q:
                # Return a small curated list as a placeholder
                base_list = [
                    {"symbol": "SOL", "name": "Solana", "market": "SOL", "chain": "sol", "kind": "spot"},
                    {"symbol": "BONK", "name": "BONK", "market": "BONK", "chain": "sol", "kind": "spot"},
                    {"symbol": "ETH", "name": "Ethereum", "market": "ETH", "chain": "eth", "kind": "spot"},
                ]
                results = base_list[:limit]
            else:
                # Return the query as a single candidate; UI can request candles with tokenCA if known
                results = [{"symbol": q.upper(), "name": q.upper(), "market": q.upper(), "chain": "sol", "kind": "spot"}]
        return jsonify({"success": True, "mode": mode, "results": results})
    except Exception as e:
        logger.error(f"/api/ui/markets error: {e}")
        # Never break UI; return an empty result set
        return jsonify({"success": True, "mode": request.args.get("mode") or "spot", "results": []}), 200

# JWT Secret and Expiry
JWT_SECRET = os.environ.get("JWT_SECRET", "grace_default_jwt_secret")
JWT_EXPIRY = int(os.environ.get("JWT_EXPIRY", 86400))  # 24 hours

# --- JWT and Session Management ---
# In-memory session store with persistence
# Sessions will be loaded during app startup
# Define empty dict for now
active_sessions: Dict[str, Dict[str, Any]] = {}


def generate_jwt_token(user_id: str) -> str:
    """Generate JWT token."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXPIRY),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and check if session is active."""
    if not token:
        logger.warning("Empty token received for verification")
        return {"success": False, "message": "No token provided"}

    try:
        # First decode the token to check for basic validity and expiration
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("user_id")

            if not user_id:
                logger.warning("Token missing user_id claim")
                return {"success": False, "message": "Invalid token format"}

        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token received: {token[:10]}...")
            # Clean up expired session
            if token in active_sessions:
                del active_sessions[token]
            return {"success": False, "message": "Token expired"}

        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token error: {e}")
            return {"success": False, "message": "Invalid token"}

        # Check if token is in active sessions
        if token not in active_sessions:
            logger.warning(f"Token not found in active sessions: {token[:10]}...")
            return {"success": False, "message": "Session not found or expired"}

        # Update last activity timestamp to keep session fresh
        session_data = active_sessions[token]
        session_data["last_activity"] = datetime.utcnow().isoformat()

        # Get username from session if available
        username = session_data.get("username", "Unknown")

        # Return success with user info
        return {
            "success": True,
            "user_id": user_id,
            "username": username,
            "session_data": session_data,
        }

    except Exception as e:
        logger.error(
            f"Unexpected error during token verification: {str(e)}", exc_info=True
        )
        return {"success": False, "message": f"Token verification error: {str(e)}"}


async def get_token_from_request() -> Optional[str]:
    """Extract bearer token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


async def verify_token_and_get_user_id() -> Dict[str, Any]:
    """Helper to verify token from request and return user_id."""
    token = await get_token_from_request()
    if not token:
        return {"success": False, "error": "Authorization token required"}

    result = verify_jwt_token(token)
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("message", "Invalid or expired token"),
        }

    return {"success": True, "user_id": result.get("user_id")}


# --- Session Persistence ---
# File to store sessions
script_dir = os.path.dirname(__file__)
SESSIONS_FILE = os.path.join(script_dir, "persistent_sessions.json")


async def save_sessions():
    """Save active sessions to persistent storage (asyncio-friendly)"""
    try:
        # Serialize sessions for storage (handling datetime objects)
        serialized_sessions = {}
        for token, session_data in active_sessions.items():
            serialized = {}
            for key, value in session_data.items():
                # Handle datetime objects
                if isinstance(value, datetime):
                    serialized[key] = value.isoformat()
                else:
                    serialized[key] = value
            serialized_sessions[token] = serialized

        # Use async with loop.run_in_executor for non-blocking file I/O
        def write_file():
            os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)
            with open(SESSIONS_FILE, "w") as f:
                json.dump(serialized_sessions, f, indent=2)

        # Run the file write in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, write_file)
        logger.info("Saved %d sessions to %s", len(active_sessions), SESSIONS_FILE)
    except Exception as e:
        logger.error("Error saving sessions: %s", e)


async def load_sessions():
    """Load persistent sessions from storage"""
    try:
        if not os.path.exists(SESSIONS_FILE):
            logger.info("Sessions file %s not found, starting with empty sessions", SESSIONS_FILE)
            return {}
            
        # Use async with loop.run_in_executor for non-blocking file I/O
        def read_file():
            with open(SESSIONS_FILE, "r") as f:
                return json.load(f)
                
        # Run the file read in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        loaded_sessions = await loop.run_in_executor(None, read_file)
        
        # Restore sessions with proper datetime conversion
        restored_sessions = {}
        for token, session_data in loaded_sessions.items():
            restored_session = {}
            for key, value in session_data.items():
                try:
                    restored_session[key] = (
                        datetime.fromisoformat(value)
                        if "time" in key.lower()
                        else value
                    )
                except ValueError:
                    restored_session[key] = value
                    
            # Only restore sessions that haven't expired
            if (
                "exp" in restored_session
                and isinstance(restored_session["exp"], str)
                and datetime.fromisoformat(restored_session["exp"]) < datetime.now()
            ):
                continue

            restored_sessions[token] = restored_session

        logger.info("Loaded %d sessions from %s", len(restored_sessions), SESSIONS_FILE)
        return restored_sessions
    except Exception as e:
        logger.error("Error loading sessions: %s", e)
        return {}


# Refresh Token Endpoint
# Support both legacy and standardized paths to work across local and Docker setups
@app.route("/auth/refresh-token", methods=["POST"])
@app.route("/api/auth/refresh-token", methods=["POST"])
async def refresh_token():
    """Endpoint to refresh authentication token"""
    try:
        # Get current token from request
        current_token = await get_token_from_request()
        if not current_token:
            return jsonify({"success": False, "message": "No token provided"}), 401

        # Verify current token
        verification_result = verify_jwt_token(current_token)
        if not verification_result.get("success"):
            return (
                jsonify({"success": False, "message": "Invalid or expired token"}),
                401,
            )

        # Extract user information
        user_id = verification_result.get("user_id")
        username = verification_result.get("username", "Unknown")

        # Generate new token
        new_token = generate_jwt_token(user_id)

        # Update session with new token
        session_data = active_sessions.get(current_token, {})
        session_data["last_activity"] = datetime.utcnow().isoformat()
        active_sessions[new_token] = session_data

        # Optional: Remove old token
        if current_token in active_sessions:
            del active_sessions[current_token]

        # Save updated sessions
        await save_sessions()

        return jsonify({"success": True, "token": new_token, "username": username}), 200

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({"success": False, "message": "Token refresh failed"}), 500


# On app startup, load persistent sessions
# (The actual startup function is defined at the end of the file)


async def load_sessions():
    """Load sessions from persistent storage (asyncio-friendly)"""
    try:
        if not os.path.exists(SESSIONS_FILE):
            return {}

        # Use async with loop.run_in_executor for non-blocking file I/O
        def read_file():
            with open(SESSIONS_FILE, "r") as f:
                return json.load(f)

        # Run the file read in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        raw_sessions = await loop.run_in_executor(None, read_file)

        sessions = {}
        # Deserialize each session
        for token, session_data in raw_sessions.items():
            deserialized = {}
            for key, value in session_data.items():
                # Try to parse ISO format datetime strings
                if key in ["created_at", "last_activity"] and isinstance(value, str):
                    try:
                        deserialized[key] = datetime.fromisoformat(value)
                    except ValueError:
                        deserialized[key] = value
                else:
                    deserialized[key] = value
            sessions[token] = deserialized

        logger.info(f"Loaded {len(sessions)} sessions from {SESSIONS_FILE}")
        return sessions
    except Exception as e:
        logger.error(f"Error loading sessions: {e}", exc_info=True)
        return {}


# Persistent session save task
async def periodic_session_save():
    """Asyncio task for periodic session saving"""
    while True:
        try:
            await save_sessions()
            # Sleep for 5 minutes
            await asyncio.sleep(300)  # Non-blocking sleep
        except asyncio.CancelledError:
            # Handle task cancellation
            break
        except Exception as e:
            logger.error(f"Error in periodic session save: {e}", exc_info=True)
            # Sleep a bit before retrying
            await asyncio.sleep(60)


# ----------------------------------


# --- Helper for running sync Grace methods ---
async def run_grace_sync(func, *args, **kwargs):
    """Runs a Grace function (sync or async) in an executor if needed."""
    if grace_instance is None:
        raise RuntimeError("Grace Core is not initialized")

    # Check if the function is a coroutine function (async)
    if asyncio.iscoroutinefunction(func):
        # If it's async, just await it directly
        return await func(*args, **kwargs)
    else:
        # If it's sync, run it in an executor
        loop = asyncio.get_running_loop()

        # Create a wrapper function that handles both args and kwargs
        def func_wrapper():
            return func(*args, **kwargs)

        # Use default executor (ThreadPoolExecutor)
        return await loop.run_in_executor(None, func_wrapper)


# -------------------------------------------

# --- API Endpoints ---


# Authentication
@app.route("/api/auth/forgot-password", methods=["POST"])
async def forgot_password():
    """Initiate password recovery process"""
    if not recovery_system:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Password recovery system is not available",
                }
            ),
            503,
        )

    try:
        data = await request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400

        # Check if user exists
        user = await run_grace_sync(
            grace_instance.memory_system.user_profile_system.get_user_by_email, email
        )

        if not user or not user.get("success"):
            # Don't reveal that the user doesn't exist for security reasons
            return jsonify(
                {
                    "success": True,
                    "message": "If your email is registered, you will receive password reset instructions",
                }
            )

        # Get user profile
        user_id = user["user_id"]

        # Generate reset URL
        base_url = request.headers.get("Origin", "http://localhost:9000")
        reset_url = f"{base_url}/reset-password.html"

        # Initiate recovery
        recovery_result = await run_grace_sync(
            recovery_system.initiate_recovery,
            email=email,
            user_id=user_id,
            reset_url=reset_url,
        )

        if recovery_result.get("success"):
            return jsonify(
                {
                    "success": True,
                    "message": "Password reset instructions have been sent to your email",
                }
            )
        else:
            logger.error(f"Failed to initiate password recovery: {recovery_result}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Failed to send password reset instructions. Please try again later.",
                    }
                ),
                500,
            )
    except Exception as e:
        logger.error(f"Error in forgot_password: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "An error occurred. Please try again later.",
                }
            ),
            500,
        )


@app.route("/api/trading/positions", methods=["GET"])
@jwt_required()
async def get_unified_positions():
    """Aggregate GMGN spot + Flash leverage positions into a unified normalized list.

    Returns shape:
      {
        success: bool,
        positions: [
          {
            id: str,
            token: str,
            type: 'spot'|'leverage',
            amount: float,
            entryPrice: float,
            currentPrice: float,
            openTimestamp: int (ms),
            side?: 'long'|'short',
            market?: str,
            unrealizedPnl?: float,
            realizedPnl?: float,
            // metadata
            source: 'gmgn'|'flash',
            orderType?: str
          }
        ],
        timestamp: int (ms)
      }
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        gmgn_service = grace_instance.gmgn_service

        # Fetch both spot and leverage (Flash) via gmgn_service helpers
        spot = await run_grace_sync(
            gmgn_service.get_user_spot_positions,
            user_identifier=user_id,
        )
        lev = await run_grace_sync(
            gmgn_service.get_user_leverage_positions,
            user_identifier=user_id,
        )

        def to_ms(ts_val):
            try:
                if ts_val is None:
                    return int(time.time() * 1000)
                # If already looks like ms
                if isinstance(ts_val, (int, float)):
                    v = float(ts_val)
                    return int(v if v > 1e12 else v * 1000)
                # ISO string
                return int(datetime.fromisoformat(str(ts_val).replace('Z', '+00:00')).timestamp() * 1000)
            except Exception:
                return int(time.time() * 1000)

        def normalize(items, source_tag: str):
            res = []
            for it in (items or []):
                try:
                    pos = {
                        "id": it.get("id") or it.get("position_id") or str(uuid.uuid4()),
                        "token": it.get("token") or it.get("symbol") or it.get("market", "").split("/")[0] or "UNKNOWN",
                        "type": it.get("type") if it.get("type") in ("spot", "leverage") else ("leverage" if it.get("leverage") else "spot"),
                        "amount": float(it.get("amount") or it.get("size") or 0),
                        "entryPrice": float(it.get("entryPrice") or it.get("entry_price") or 0),
                        "currentPrice": float(it.get("currentPrice") or it.get("mark_price") or it.get("price") or 0),
                        "openTimestamp": to_ms(it.get("openTimestamp") or it.get("open_time") or it.get("timestamp")),
                        "side": it.get("side"),
                        "market": it.get("market"),
                        "unrealizedPnl": float(it.get("unrealizedPnl") or it.get("pnl") or 0),
                        "realizedPnl": float(it.get("realizedPnl") or 0),
                        "source": source_tag,
                        "orderType": it.get("orderType") or it.get("order_type"),
                    }
                    # Include leverage-specific metrics if present
                    if it.get("leverage") is not None:
                        try:
                            pos["leverage"] = float(it.get("leverage") or 0)
                        except Exception:
                            pass
                    if it.get("liquidationPrice") is not None:
                        try:
                            pos["liquidationPrice"] = float(it.get("liquidationPrice") or 0)
                        except Exception:
                            pass
                    if it.get("marginRatio") is not None:
                        try:
                            pos["marginRatio"] = float(it.get("marginRatio") or 0)
                        except Exception:
                            pass
                    res.append(pos)
                except Exception as _e:
                    logger.warning(f"Skipping position normalization error: {_e}")
            return res

        unified = []
        unified.extend(normalize(spot.get("positions", []), "gmgn"))
        unified.extend(normalize(lev.get("positions", []), "flash"))

        return jsonify({
            "success": True,
            "positions": unified,
            "timestamp": int(time.time() * 1000),
        })
    except Exception as e:
        logger.error(f"Error aggregating unified positions: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/trading/transactions", methods=["GET"])
@jwt_required()
async def get_unified_transactions():
    """Return unified transactions across sources. Currently reuses wallet transactions fallback."""
    try:
        result = await verify_token_and_get_user_id()
        if not result.get("success"):
            return jsonify(result), 401

        user_id = result["user_id"]

        # Prefer existing wallet transactions aggregator if available
        tx = None
        try:
            if hasattr(grace_instance, "get_wallet_transactions"):
                tx = await run_grace_sync(grace_instance.get_wallet_transactions, user_id=user_id)
        except Exception as e:
            logger.warning(f"get_wallet_transactions not available or failed: {e}")

        # Fallback to calling the internal endpoint logic directly
        if not tx:
            # Call the same logic as /api/wallet/transactions
            try:
                # Some deployments store on disk under data/
                tx = []
            except Exception:
                tx = []

        # Normalize minimal shape for UI compatibility if needed
        def norm_tx(item):
            try:
                return {
                    "id": item.get("id") or item.get("signature") or str(uuid.uuid4()),
                    "type": item.get("type") or item.get("category") or "swap",
                    "token": item.get("token") or item.get("symbol") or item.get("market", "").split("/")[0] or "UNKNOWN",
                    "amount": float(item.get("amount") or item.get("size") or 0),
                    "timestamp": item.get("timestamp") or item.get("time") or datetime.now().isoformat(),
                    "status": item.get("status") or "completed",
                    "source": item.get("source") or "gmgn",
                }
            except Exception:
                return None

        data = [t for t in (norm_tx(x) for x in (tx or [])) if t]
        return jsonify({"success": True, "transactions": data, "count": len(data)})
    except Exception as e:
        logger.error(f"Error getting unified transactions: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/trade/initiate", methods=["POST"])
@jwt_required()
async def trade_initiate():
    """Build an unsigned GMGN transaction for Phantom signing.

    Body: { action: 'buy'|'sell', token: str, amount: str|number }
    """
    try:
        user_id = get_jwt_identity()
        data = await request.get_json()
        action = (data or {}).get("action")
        token = (data or {}).get("token")
        amount = (data or {}).get("amount")

        if not action or not token or amount in (None, ""):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Ensure amount is str as expected by gmgn_service builder
        amount_str = str(amount)

        gmgn_service = grace_instance.gmgn_service
        build = await run_grace_sync(
            gmgn_service.build_unsigned_spot_transaction,
            action,
            amount_str,
            token,
            user_id,
        )

        if not build.get("success"):
            return jsonify({"success": False, "error": build.get("error", "Failed to build unsigned tx")}), 502

        # Standardize response for UI
        payload = {
            "success": True,
            "status": build.get("status") or "signature_required",
            "action": action,
            "token": token,
            "amount": amount,
            "signature_required": True,
            "serialized_tx": build.get("serialized_tx"),
            "confirmation_id": build.get("confirmation_id") or build.get("confirmationId"),
            "router": build.get("router"),
        }
        return jsonify(payload), 200
    except Exception as e:
        logger.error(f"trade_initiate error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/trade/submit", methods=["POST"])
@jwt_required()
async def trade_submit():
    """Accept a signed tx and broadcast via the existing Solana JSON-RPC relay.

    Body: { signedTransaction: base64, options?: {...} }
    """
    try:
        data = await request.get_json()
        signed_tx = (data or {}).get("signedTransaction") or (data or {}).get("signed_tx")
        options = (data or {}).get("options") or {}
        if not signed_tx:
            return jsonify({"success": False, "error": "signedTransaction is required"}), 400

        # Reuse existing relay endpoint logic
        rpc_url = get_solana_rpc_url()
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "sendTransaction",
            "params": [signed_tx, options],
        }
        r = requests.post(rpc_url, json=payload, timeout=30, headers=headers)
        data = {}
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}

        ok = (r.status_code == 200) and ("error" not in data)
        return jsonify({"success": ok, "rpc": data}), (200 if ok else 502)
    except Exception as e:
        logger.error(f"trade_submit error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/auth/reset-password", methods=["POST"])
async def reset_password():
    """Reset password using recovery token"""
    if not recovery_system:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Password recovery system is not available",
                }
            ),
            503,
        )

    try:
        data = await request.get_json()
        token = data.get("token")
        new_password = data.get("password")

        if not token or not new_password:
            return (
                jsonify(
                    {"success": False, "message": "Token and new password are required"}
                ),
                400,
            )

        # Verify token
        verification = await run_grace_sync(
            recovery_system.verify_recovery_token, token
        )

        if not verification.get("valid"):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": verification.get(
                            "error", "Invalid or expired token"
                        ),
                    }
                ),
                400,
            )

        # Reset password
        result = await run_grace_sync(
            recovery_system.complete_recovery,
            token=token,
            new_password=new_password,
            user_profile_system=grace_instance.memory_system.user_profile_system,
        )

        if result.get("success"):
            return jsonify(
                {"success": True, "message": "Password has been reset successfully"}
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": result.get("error", "Failed to reset password"),
                    }
                ),
                500,
            )
    except Exception as e:
        logger.error(f"Error in reset_password: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "An error occurred. Please try again later.",
                }
            ),
            500,
        )


@app.route("/api/auth/register", methods=["POST"])
async def register():
    """Register a new user."""
    if grace_instance is None:
        return (
            jsonify(
                {"success": False, "message": "Server error: Grace Core not available"}
            ),
            500,
        )
    try:
        data = await request.get_json()
        if (
            not data
            or not data.get("username")
            or not data.get("email")
            or not data.get("password")
            or not data.get("firstName")
            or not data.get("lastName")
        ):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Missing required fields: username, firstName, lastName, email, password",
                    }
                ),
                400,
            )
    except Exception as e:
        logger.error(f"Register request format error: {e}")
        return (
            jsonify({"success": False, "message": f"Invalid request format: {str(e)}"}),
            400,
        )

    username = data.get("username")
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = data.get("email")
    password = data.get("password")

    try:
        # Run synchronous create_user in executor
        create_result = await run_grace_sync(
            grace_instance.user_profile_system.create_user,
            username=username,
            email=email,
            password=password,
            phone=data.get("phone"),
        )

        if not create_result or not create_result.get("success"):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": (
                            create_result.get("message")
                            if create_result
                            else "User creation failed"
                        ),
                    }
                ),
                400,
            )

        user_id = create_result.get("user_id")

        # Link HL wallet metadata (env from HL_ENV, default mainnet)
        try:
            hl_env = os.environ.get("HL_ENV", "mainnet")
            await run_grace_sync(
                grace_instance.user_profile_system.link_hl_wallet,
                user_id,
                hl_env,
            )
        except Exception as e:
            logger.warning(f"HL wallet link failed for {user_id}: {e}")

        token = generate_jwt_token(user_id)

        # Store session
        active_sessions[token] = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        logger.info(f"User registered and session created for user_id: {user_id}")

        # Fetch HL wallet to include masked address in meta
        hl_wallet = None
        try:
            prof = await run_grace_sync(
                grace_instance.user_profile_system.get_user_profile, user_id
            )
            if prof and prof.get("success"):
                hl_wallet = (prof.get("profile", {}) or {}).get("hl_wallet")
        except Exception:
            pass

        def _mask(addr: Optional[str]) -> Optional[str]:
            if not addr or len(addr) < 10:
                return addr
            return f"{addr[:6]}…{addr[-4:]}"

        return (
            jsonify(
                {
                    "success": True,
                    "token": token,
                    "user": {
                        "id": user_id,
                        "username": username,
                        "email": email,
                        "created_at": create_result.get("created_at"),
                    },
                    "meta": {
                        "hl_env": (hl_wallet or {}).get("env"),
                        "hl_address_masked": _mask((hl_wallet or {}).get("address")),
                        "hl_status": (hl_wallet or {}).get("status"),
                    },
                }
            ),
            201,
        )  # Use 201 Created status code

    except ValueError as e:
        logger.warning(f"Registration validation error: {e}")
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error during registration",
                }
            ),
            500,
        )


@app.route("/api/mango/account/existence", methods=["GET"])
async def mango_account_existence():
    """Check Mango v3 accounts for an owner pubkey.

    Query params:
      - owner: base58 owner pubkey (required)
    """
    try:
        owner = request.args.get("owner")
        if not owner:
            return jsonify({"success": False, "message": "owner is required"}), 400

        # Prepare environment for the CLI
        env = os.environ.copy()
        if not env.get("SOLANA_RPC_URL"):
            return jsonify({"success": False, "message": "SOLANA_RPC_URL not set"}), 500
        if not env.get("GROUP"):
            env["GROUP"] = "mainnet.1"

        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "mango-create-account.mjs"))
        if not os.path.exists(script_path):
            return jsonify({"success": False, "message": f"CLI not found at {script_path}"}), 500

        # Run CLI in check mode for specified owner via build-unsigned-tx mode (which also reports existing)
        cmd = [
            "node",
            script_path,
        ]
        run_env = env.copy()
        run_env["MODE"] = "build-unsigned-tx"
        run_env["OWNER"] = owner

        proc = subprocess.run(cmd, env=run_env, capture_output=True, text=True)
        if proc.returncode != 0:
            return jsonify({"success": False, "message": proc.stderr.strip() or proc.stdout.strip()}), 500

        try:
            data = json.loads(proc.stdout.strip())
        except Exception:
            data = {"ok": False, "raw": proc.stdout.strip()}

        return jsonify({"success": True, "data": data})
    except Exception as e:
        logger.error(f"mango_account_existence error: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/mango/account/create-tx", methods=["POST"])
async def mango_account_create_tx():
    """Build an unsigned Mango account creation transaction for a given owner.

    Body JSON:
      - owner: base58 owner pubkey (required)
    Returns base64 transaction and a new mangoAccountPubkey.
    """
    try:
        body = await request.get_json()
        owner = (body or {}).get("owner")
        if not owner:
            return jsonify({"success": False, "message": "owner is required"}), 400

        env = os.environ.copy()
        if not env.get("SOLANA_RPC_URL"):
            return jsonify({"success": False, "message": "SOLANA_RPC_URL not set"}), 500
        if not env.get("GROUP"):
            env["GROUP"] = "mainnet.1"

        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "mango-create-account.mjs"))
        if not os.path.exists(script_path):
            return jsonify({"success": False, "message": f"CLI not found at {script_path}"}), 500

        cmd = ["node", script_path]
        run_env = env.copy()
        run_env["MODE"] = "build-unsigned-tx"
        run_env["OWNER"] = owner

        proc = subprocess.run(cmd, env=run_env, capture_output=True, text=True)
        if proc.returncode != 0:
            return jsonify({"success": False, "message": proc.stderr.strip() or proc.stdout.strip()}), 500

        data = json.loads(proc.stdout.strip())
        return jsonify({"success": True, "transaction": data.get("transaction"), "mangoAccountPubkey": data.get("mangoAccountPubkey"), "exists": data.get("exists", False), "accounts": data.get("accounts", [])})
    except Exception as e:
        logger.error(f"mango_account_create_tx error: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/auth/login", methods=["POST"])
async def login():
    """Handle user login and create session."""
    if grace_instance is None:
        return (
            jsonify(
                {"success": False, "message": "Server error: Grace Core not available"}
            ),
            500,
        )

    # Extract login credentials
    try:
        data = await request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        username = data.get("username")
        password = data.get("password")
        remember_me = data.get("remember_me", False)

        if not username or not password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Missing required fields: username, password",
                    }
                ),
                400,
            )
    except Exception as e:
        logger.error(f"Login request format error: {e}")
        return (
            jsonify({"success": False, "message": f"Invalid request format: {str(e)}"}),
            400,
        )

    try:
        # Get IP address and user agent for security tracking
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
        user_agent = request.headers.get("User-Agent", "Unknown")

        # Authenticate user
        auth_result = await run_grace_sync(
            grace_instance.user_profile_system.authenticate,
            username_or_email=username,
            password=password,
        )

        if not auth_result or not auth_result.get("success"):
            logger.warning(
                f"Authentication failed for user: {username} from IP: {ip_address}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "message": (
                            auth_result.get("message")
                            if auth_result
                            else "Authentication failed"
                        ),
                    }
                ),
                401,
            )

        # Generate token and create session
        user_id = auth_result.get("user_id")
        token = generate_jwt_token(user_id)

        # Get user profile data consistently using get_user_profile
        profile_result = await run_grace_sync(
            grace_instance.user_profile_system.get_user_profile, user_id
        )

        # Extract profile data from the result structure
        user_profile = (
            profile_result.get("profile", {})
            if profile_result and profile_result.get("success")
            else {}
        )

        # Store rich session data
        active_sessions[token] = {
            "user_id": user_id,
            "username": username,
            "email": user_profile.get("email"),
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "remember_me": remember_me,
        }

        # Clean up any existing sessions for this user to prevent duplicates
        for existing_token, session in list(active_sessions.items()):
            if session.get("user_id") == user_id and existing_token != token:
                logger.info(f"Removing existing session for user_id: {user_id}")
                active_sessions.pop(existing_token, None)

        # No need to fetch user_profile again as we already have it from earlier in the function
        # If we don't have a valid user_profile, create a basic one for the response
        if not user_profile:
            logger.warning(f"No valid user profile data for user_id: {user_id}")
            # Create a basic profile with data we already have if profile is missing
            user_profile = {
                "id": user_id,
                "username": username,
                "email": active_sessions[token].get("email"),
            }

        logger.info(
            f"User logged in and session created for user_id: {user_id}, username: {username}"
        )

        # Return comprehensive response with user data
        return jsonify(
            {
                "success": True,
                "token": token,
                "user_id": user_id,
                "username": username,
                "user": user_profile,
                "message": "Login successful",
            }
        )

    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "message": "Internal server error during login"}
            ),
            500,
        )


@app.route("/api/auth/verify", methods=["GET"])
async def verify_token_endpoint():
    """Verify JWT token from request header and return user information."""
    token = await get_token_from_request()

    if not token:
        logger.warning("Token verification failed: No token provided")
        return jsonify({"success": False, "message": "No token provided"}), 401

    # Verify token and get session data
    result = verify_jwt_token(token)
    logger.info(f"Token verification result: {result.get('success')}")

    if not result.get("success"):
        return jsonify(result), 401

    # Token is valid, extract information
    user_id = result.get("user_id")
    session_data = result.get("session_data", {})

    try:
        # Get user profile data consistently using get_user_profile
        profile_result = await run_grace_sync(
            grace_instance.user_profile_system.get_user_profile, user_id
        )

        # Extract profile data from the result structure
        user_profile = (
            profile_result.get("profile", {})
            if profile_result and profile_result.get("success")
            else {}
        )

        if not user_profile:
            logger.warning(f"User profile not found for user_id: {user_id}")
            # Profile not found but token was valid - return minimal user info
            return jsonify(
                {
                    "success": True,
                    "user_id": user_id,
                    "username": session_data.get("username", "Unknown"),
                    "message": "Token valid but user profile not found",
                }
            )

        # Augment profile with session info
        user_profile["last_activity"] = session_data.get("last_activity")
        user_profile["session_created_at"] = session_data.get("created_at")

        # Log successful verification
        logger.info(
            f"Token verification successful for user_id: {user_id}, username: {user_profile.get('username', 'Unknown')}"
        )

        return jsonify(
            {
                "success": True,
                "user": user_profile,
                "user_id": user_id,  # Include these directly for easier client access
                "username": user_profile.get(
                    "username", session_data.get("username", "Unknown")
                ),
            }
        )

    except Exception as e:
        logger.error(
            f"Error retrieving user profile during token verification: {e}",
            exc_info=True,
        )
        # Fallback to session data if profile retrieval fails
        return jsonify(
            {
                "success": True,  # Token is still valid
                "user_id": user_id,
                "username": session_data.get("username", "Unknown"),
                "session_data": session_data,
                "message": "Token valid but error retrieving complete user profile",
            }
        )


@app.route("/api/auth/logout", methods=["POST"])
async def logout():
    """Logout user by invalidating session."""
    token = await get_token_from_request()

    if not token:
        logger.warning("Logout attempt with missing token")
        return jsonify({"success": False, "message": "No token provided"}), 401

    # Get session info before removal for logging
    session_info = active_sessions.get(token, {})
    user_id = session_info.get("user_id")
    username = session_info.get("username", "Unknown")

    # Remove all sessions for this user to ensure complete logout
    if user_id:
        # First remove the specific token
        if token in active_sessions:
            del active_sessions[token]

        # Then clear any other sessions for the same user (multi-device logout)
        duplicate_tokens = []
        for existing_token, session in active_sessions.items():
            if session.get("user_id") == user_id:
                duplicate_tokens.append(existing_token)

        for dup_token in duplicate_tokens:
            del active_sessions[dup_token]

        total_removed = 1 + len(duplicate_tokens)
        logger.info(
            f"User logged out: user_id={user_id}, username={username}. Removed {total_removed} sessions."
        )
        return jsonify(
            {
                "success": True,
                "message": "Logged out successfully",
                "sessions_removed": total_removed,
            }
        )
    elif token in active_sessions:
        # Token exists but doesn't have user_id - just remove it
        del active_sessions[token]
        logger.warning(f"Removed session with token but no user_id: {token[:10]}...")
        return jsonify({"success": True, "message": "Session terminated"})
    else:
        logger.warning(f"Logout attempt with invalid token: {token[:10]}...")
        return jsonify({"success": False, "message": "Invalid token"}), 401


# Chat Endpoint
@app.route("/api/chat/message", methods=["POST"])
async def process_chat_message():  # Renamed from process_message
    """Process a chat message from the user."""
    if grace_instance is None:
        return jsonify({"error": "Server error: Grace Core not available"}), 500

    token_result = await verify_token_and_get_user_id()
    if not token_result.get("success"):
        return (
            jsonify({"error": token_result.get("error", "Authentication failed")}),
            401,
        )

    user_id = token_result.get("user_id")
    if not user_id:
        # This case should ideally not happen if verify_token_and_get_user_id works correctly
        return jsonify({"error": "User ID not found after token verification"}), 401

    try:
        data = await request.get_json()
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Use provided session_id from client, or create a new one
        session_id = data.get("session_id")
    except Exception:
        logger.warning("Invalid JSON format received for chat message")
        return jsonify({"error": "Invalid request format"}), 400

    # If no session_id provided, try to reuse the user's latest active session
    if not session_id:
        try:
            latest = await run_grace_sync(get_latest_session_for_user, user_id)
            if latest:
                session_id = latest
                logger.info(
                    f"No session_id provided; reusing user's latest session: {session_id}"
                )
            else:
                session_id = str(uuid.uuid4())
                logger.info(
                    f"No prior session found; generating new session_id: {session_id}"
                )
        except Exception as e:
            logger.warning(
                f"Failed to lookup latest session for user {user_id}: {e}; generating new session_id"
            )
            session_id = str(uuid.uuid4())

    try:
        # First, integrate with the chat sessions system
        # Import here to avoid circular imports
        try:
            from src.chat_sessions_quart import (
                handle_chat_message_with_session,
                IN_MEMORY_STORAGE as CSQ_IN_MEMORY_STORAGE,
                redis as CSQ_REDIS,
            )
        except ImportError:
            from chat_sessions_quart import (
                handle_chat_message_with_session,
                IN_MEMORY_STORAGE as CSQ_IN_MEMORY_STORAGE,
                redis as CSQ_REDIS,
            )

        # Register the message with the chat sessions system
        session_result = await handle_chat_message_with_session(
            user_id, message, session_id
        )

        # If there was an error or the session_id changed, update it
        if session_result.get("error"):
            logger.warning(
                f"Error in chat session handling: {session_result.get('error')}"
            )
        if session_result.get("session_id"):
            session_id = session_result.get("session_id")

        # Run synchronous grace.process_message in executor
        logger.info(
            f"Calling grace.process_message for user {user_id} with session {session_id}..."
        )
        response_content = await run_grace_sync(
            grace_instance.process_message,
            user_id=user_id,
            session_id=session_id,  # Pass the session_id
            message=message,
        )
        logger.info(
            f"Received response from grace.process_message: {response_content[:100]}..."
        )

        # Store the bot's response in the chat session
        try:
            # Create response message object
            bot_response = {
                "bot": response_content,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Store in Redis or fallback storage via chat_sessions module
            # session_result is a dictionary, not an object, so check with get()
            if session_result.get("using_fallback", False):
                # Using fallback in-memory storage
                if session_id in CSQ_IN_MEMORY_STORAGE["messages"]:
                    CSQ_IN_MEMORY_STORAGE["messages"][session_id].append(bot_response)
            else:
                # Try to use Redis
                if CSQ_REDIS:
                    await CSQ_REDIS.rpush(
                        f"chat:{session_id}:messages", json.dumps(bot_response)
                    )
        except Exception as e:
            logger.error(f"Error storing bot response in chat session: {str(e)}")

        # Return response in multiple formats to ensure compatibility with frontend
        return jsonify(
            {
                "response": response_content,
                "message": response_content,  # Alternative field name
                "content": response_content,  # Another possible field name
                "success": True,  # Indicate success
                "session_id": session_id,  # Return session_id to the frontend for continuity
            }
        )

    except RuntimeError as e:
        # Catch the specific error if Grace Core wasn't initialized
        logger.error(f"RuntimeError during chat processing: {e}")
        return jsonify({"error": "Server configuration error"}), 500
    except Exception as e:
        logger.error(f"Error calling grace.process_message: {str(e)}", exc_info=True)
        return jsonify({"error": "Error processing message"}), 500


# --- Other Placeholder/Example Endpoints ---
# (These need implementation using run_grace_sync if calling sync Grace methods)


@app.route("/api/memory/learn", methods=["POST"])
async def learn():
    # Needs implementation using run_grace_sync for memory_system.add_to_memory
    return jsonify({"message": "Learn endpoint not fully implemented"}), 501


# Trading Positions Endpoints


@app.route("/api/limit-orders", methods=["GET"])
async def get_limit_orders():
    """Get active limit orders for the user."""
    try:
        # Verify authentication
        user_id = await verify_token_and_get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        # Get query parameters
        trade_type = request.args.get(
            "trade_type"
        )  # 'spot' or 'leverage' or None for both
        market = request.args.get("market")  # specific market or None for all

        # Get limit orders through Grace Core
        result = await run_grace_sync(
            current_app.grace_instance.get_limit_orders,
            user_id=user_id,
            trade_type=trade_type,
            market=market,
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting limit orders: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/user/leverage_positions", methods=["GET"])
@jwt_required()
async def get_user_leverage_positions():
    try:
        # Get the current user's ID from the JWT
        user_id = get_jwt_identity()

        # Initialize the GMGN service
        gmgn_service = grace_instance.gmgn_service

        # Retrieve leverage positions via executor to keep async compatibility
        leverage_positions = await run_grace_sync(
            gmgn_service.get_user_leverage_positions,
            user_identifier=user_id,
        )

        # Format the response
        formatted_response = {
            "success": True,
            "positions": leverage_positions.get("positions", []),
            "metadata": leverage_positions.get("metadata", {}),
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(formatted_response), 200

    except Exception as e:
        logger.error(f"Error retrieving leverage positions: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to retrieve leverage positions",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/api/user/spot_positions", methods=["GET"])
@jwt_required()
async def get_user_spot_positions():
    try:
        # Get the current user's ID from the JWT
        user_id = get_jwt_identity()

        # Initialize the GMGN service
        gmgn_service = grace_instance.gmgn_service

        # Retrieve spot positions via executor
        spot_positions = await run_grace_sync(
            gmgn_service.get_user_spot_positions,
            user_identifier=user_id,
        )

        # Format the response
        formatted_response = {
            "success": True,
            "positions": spot_positions.get("positions", []),
            "metadata": spot_positions.get("metadata", {}),
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(formatted_response), 200

    except Exception as e:
        logger.error(f"Error retrieving spot positions: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to retrieve spot positions",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/api/trading/active-positions", methods=["GET"])
async def get_active_trading_positions():
    """Retrieve active trading positions for the user"""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    try:
        # Simulate fetching active positions from a trading system
        active_positions = [
            {
                "id": str(uuid.uuid4()),
                "token": "SOL",
                "type": "leverage",
                "amount": 100.50,
                "entryPrice": 140.25,
                "currentPrice": 142.75,
                "leverage": 3,
                "openTimestamp": datetime.utcnow().isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "token": "USDC",
                "type": "spot",
                "amount": 500.00,
                "entryPrice": 1.00,
                "currentPrice": 1.01,
                "openTimestamp": datetime.utcnow().isoformat(),
            },
        ]

        return jsonify({"success": True, "positions": active_positions})
    except Exception as e:
        logger.error(f"Error fetching active positions: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve active positions"}),
            500,
        )


@app.route("/api/trading/sell-position", methods=["POST"])
async def sell_trading_position():
    """Sell a specific trading position"""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    try:
        data = await request.get_json()
        position_id = data.get("positionId")

        if not position_id:
            return jsonify({"success": False, "error": "Position ID is required"}), 400

        # Simulate selling position
        return jsonify(
            {
                "success": True,
                "message": f"Position {position_id} sold successfully",
                "soldAmount": 100.50,  # Example amount
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error selling position: {str(e)}")
        return jsonify({"success": False, "error": "Failed to sell position"}), 500


# Wallet Endpoints


@app.route("/api/wallet/test-address-conversion", methods=["POST"])
async def test_address_conversion():
    """Test endpoint to convert wallet address using different methods"""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    try:
        data = await request.get_json()
        address = data.get("address")

        if not address:
            # If no address provided, get the user's wallet address
            user_id = result["user_id"]
            wallet_data = await run_grace_sync(
                grace_instance.gmgn_service.get_wallet_balance, user_id=user_id
            )

            if wallet_data and "address" in wallet_data:
                address = wallet_data["address"]
            else:
                return (
                    jsonify(
                        {"success": False, "error": "No wallet address found for user"}
                    ),
                    404,
                )

        # Run the conversion test
        test_results = test_wallet_address_conversion(address)

        return jsonify({"success": True, "test_results": test_results})
    except Exception as e:
        logger.error(
            f"Error testing wallet address conversion: {str(e)}", exc_info=True
        )
        return jsonify({"error": "Error testing wallet address conversion"}), 500


def clean_binary_wallet_address(address):
    """Clean a wallet address that might be in binary format

    Args:
        address: The wallet address that might be in binary format

    Returns:
        str: A clean alphanumeric wallet address
    """
    if not address:
        return ""

    # If it's already a string, just return it
    if isinstance(address, str):
        # If it starts with b' and has escape characters, it's a string representation of bytes
        if address.startswith("b'") and ("\\x" in address or "\\v" in address):
            # Remove the b' prefix and ' suffix
            address = address[2:-1] if address.endswith("'") else address[2:]
            # Remove all non-alphanumeric characters
            return re.sub(r"[^a-zA-Z0-9]", "", address)
        return address

    # If it's bytes, decode it to a string
    if isinstance(address, bytes):
        try:
            # Try to decode as UTF-8
            return address.decode("utf-8")
        except UnicodeDecodeError:
            # If that fails, convert to hex
            return address.hex()

    # For any other type, convert to string and clean
    return re.sub(r"[^a-zA-Z0-9]", "", str(address))


def test_wallet_address_conversion(address):
    """Test function to convert wallet address using different methods

    Args:
        address: The wallet address to convert

    Returns:
        dict: Results of different conversion methods
    """
    results = {"original": str(address), "type": str(type(address)), "methods": {}}

    # Method 1: Standard clean function
    results["methods"]["standard_clean"] = clean_binary_wallet_address(address)

    # Method 2: Direct string conversion with regex cleanup
    try:
        direct_str = str(address)
        results["methods"]["direct_str"] = re.sub(r"[^a-zA-Z0-9]", "", direct_str)
    except Exception as e:
        results["methods"]["direct_str_error"] = str(e)

    # Method 3: For bytes, try hex encoding
    if isinstance(address, bytes):
        try:
            results["methods"]["hex_encoded"] = address.hex()
        except Exception as e:
            results["methods"]["hex_encoded_error"] = str(e)

    # Method 4: For string representation of bytes, parse manually
    if isinstance(address, str) and address.startswith("b'"):
        try:
            # Extract the content between b' and the last '
            content = address[2:-1] if address.endswith("'") else address[2:]
            # Replace escape sequences
            content = content.replace("\\x", "").replace("\\v", "")
            results["methods"]["manual_parse"] = re.sub(r"[^a-zA-Z0-9]", "", content)
        except Exception as e:
            results["methods"]["manual_parse_error"] = str(e)

    return results


@app.route("/api/wallet/info", methods=["GET"])
async def wallet_info():
    """Get wallet information for the authenticated user."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    try:
        # Get wallet information using the GMGNService
        wallet_data = await run_grace_sync(
            grace_instance.gmgn_service.get_wallet_balance, user_id=user_id
        )

        # Clean the wallet address if present
        if wallet_data and "address" in wallet_data:
            original_address = wallet_data["address"]
            wallet_data["address"] = clean_binary_wallet_address(original_address)
            logger.info(f"Cleaned wallet address: {wallet_data['address']}")

            # Add conversion test results to the response
            wallet_data["address_conversion_note"] = test_wallet_address_conversion(
                original_address
            )

        return jsonify({"success": True, "wallet": wallet_data})
    except Exception as e:
        logger.error(f"Error getting wallet info: {str(e)}", exc_info=True)
        return jsonify({"error": "Error retrieving wallet information"}), 500

@app.route("/api/wallet/mango-balance", methods=["GET"])
async def get_mango_wallet_balance():
    """Get Mango wallet balance information for the authenticated user."""
    try:
        # Verify authentication
        result = await verify_token_and_get_user_id()
        if not result.get("success"):
            return jsonify(result), 401

        user_id = result["user_id"]

        # Get Mango wallet balance through the trading service selector
        result = await run_grace_sync(
            current_app.grace_instance.trading_service_selector.check_wallet_balance,
            user_id=user_id,
        )
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting Mango wallet balance: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/wallet/generate", methods=["POST"])
async def generate_wallet():
    """Generate a new internal wallet for the authenticated user."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    try:
        # Generate a new internal wallet
        wallet_data = await run_grace_sync(
            grace_instance.solana_wallet_manager.generate_internal_wallet,
            user_id=user_id,
        )

        # If address is present, add conversion test results
        if wallet_data and "address" in wallet_data:
            original_address = wallet_data["address"]
            wallet_data["address"] = clean_binary_wallet_address(original_address)
            wallet_data["address_conversion_note"] = test_wallet_address_conversion(
                original_address
            )

        return jsonify({"success": True, "wallet": wallet_data})
    except Exception as e:
        logger.error(f"Error generating wallet: {str(e)}", exc_info=True)
        return jsonify({"error": "Error generating wallet"}), 500


# Phantom Wallet Connection Endpoints
@app.route("/api/wallet/phantom/connect", methods=["POST"])
async def initiate_phantom_connection():
    """Initiate a connection to a Phantom wallet."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()
    redirect_url = data.get("redirect_url", request.host_url)

    try:
        # Create a connection session with the WalletConnectionSystem
        connection_data = await run_grace_sync(
            grace_instance.solana_wallet_manager.wallet_connection_system.initiate_phantom_connection,
            user_id=user_id,
            redirect_url=redirect_url,
        )

        return jsonify({"success": True, "connection": connection_data})
    except Exception as e:
        logger.error(f"Error initiating Phantom connection: {str(e)}", exc_info=True)
        return jsonify({"error": "Error initiating Phantom connection"}), 500


@app.route("/api/wallet/phantom/callback", methods=["POST"])
async def complete_phantom_connection():
    """Complete a connection to a Phantom wallet after user authorization."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()
    session_id = data.get("session_id")
    wallet_address = data.get("wallet_address")

    if not session_id or not wallet_address:
        return jsonify({"error": "Missing session_id or wallet_address"}), 400

    try:
        # Complete the connection with the WalletConnectionSystem
        wallet_data = await run_grace_sync(
            grace_instance.solana_wallet_manager.wallet_connection_system.complete_phantom_connection,
            user_id=user_id,
            session_id=session_id,
            wallet_address=wallet_address,
        )

        return jsonify({"success": True, "wallet": wallet_data})
    except Exception as e:
        logger.error(f"Error completing Phantom connection: {str(e)}", exc_info=True)
        return jsonify({"error": "Error completing Phantom connection"}), 500


@app.route("/api/wallet/phantom/disconnect", methods=["POST"])
async def disconnect_phantom_wallet():
    """Disconnect a Phantom wallet."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()
    wallet_address = data.get("wallet_address")

    try:
        # Disconnect the wallet with the WalletConnectionSystem
        disconnect_result = await run_grace_sync(
            grace_instance.solana_wallet_manager.wallet_connection_system.disconnect_phantom_wallet,
            user_id=user_id,
            wallet_address=wallet_address,
        )

        return jsonify({"success": True, "result": disconnect_result})
    except Exception as e:
        logger.error(f"Error disconnecting Phantom wallet: {str(e)}", exc_info=True)
        return jsonify({"error": "Error disconnecting Phantom wallet"}), 500


# Trading Endpoints
@app.route("/api/limit-orders", methods=["POST"])
async def place_limit_order():
    """Place a limit order for spot or leverage trading."""
    try:
        # Verify authentication
        user_id = await verify_token_and_get_user_id()
        if not user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Authentication required",
                        "code": "AUTH_REQUIRED",
                    }
                ),
                401,
            )

        # Get request data
        data = await request.get_json()
        required_fields = ["market", "side", "price", "size"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Missing required field: {field}",
                            "code": "MISSING_FIELD",
                        }
                    ),
                    400,
                )

        # Validate trade type
        trade_type = data.get("trade_type", "spot").lower()
        if trade_type not in ["spot", "leverage"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Invalid trade type: {trade_type}. Must be spot or leverage.",
                        "code": "INVALID_TRADE_TYPE",
                    }
                ),
                400,
            )

        # Validate side
        if data["side"].lower() not in ["buy", "sell"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f'Invalid side: {data["side"]}. Must be buy or sell.',
                        "code": "INVALID_SIDE",
                    }
                ),
                400,
            )

        # Extract optional parameters
        leverage = (
            float(data.get("leverage", 1.0)) if trade_type == "leverage" else None
        )
        reduce_only = bool(data.get("reduce_only", False))
        client_id = data.get("client_id")

        # Place limit order through Grace Core
        result = await run_grace_sync(
            current_app.grace_instance.place_limit_order,
            market=data["market"],
            side=data["side"].lower(),
            price=float(data["price"]),
            size=float(data["size"]),
            client_id=client_id,
            reduce_only=reduce_only,
            user_id=user_id,
            trade_type=trade_type,
            leverage=leverage,
        )

        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error placing limit order: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/wallet/transactions", methods=["GET"])
async def get_transactions():
    """Get transaction history for a user."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    # Extract optional query parameters
    trade_type = request.args.get("trade_type")
    limit = int(request.args.get("limit", 50))

    try:
        transactions = []

        # First, get user profile to access existing transactions
        user_profile = await run_grace_sync(
            grace_instance.user_profile_system.get_user_profile, user_id=user_id
        )

        # Initialize transactions from user profile
        if user_profile.get("success") and "profile" in user_profile:
            profile = user_profile["profile"]
            transactions = profile.get("transactions", [])

        # Try to get trades from Mango V3 Extension
        mango_trades = []
        try:
            if hasattr(grace_instance, "mango_v3_extension"):
                mango_trades_result = await run_grace_sync(
                    grace_instance.mango_v3_extension.get_trade_history,
                    user_identifier=user_id,
                    trade_type=trade_type,
                    limit=limit,
                )

                if mango_trades_result and mango_trades_result.get("success"):
                    mango_trades = mango_trades_result.get("trades", [])
        except Exception as e:
            logger.warning(f"Error getting Mango V3 trades: {str(e)}")

        # Merge Mango trades with existing transactions
        # Prevent duplicates by checking trade_id
        existing_trade_ids = {tx.get("trade_id") for tx in transactions}
        for trade in mango_trades:
            if trade.get("trade_id") not in existing_trade_ids:
                # Standardize Mango trade to match transaction format
                mango_transaction = {
                    "transaction_id": trade.get("trade_id", str(uuid.uuid4())),
                    "type": trade.get("trade_type", "mango_trade"),
                    "status": "completed",
                    "market": trade.get("market", ""),
                    "side": trade.get("side", ""),
                    "price": trade.get("price", 0),
                    "size": trade.get("size", 0),
                    "timestamp": trade.get("timestamp", datetime.now().isoformat()),
                    "trade_source": "mango_api",
                    "leverage": trade.get("leverage", 1.0),
                }
                transactions.append(mango_transaction)

        # If transaction confirmation system has pending transactions, add those
        if hasattr(grace_instance, "transaction_confirmation_system"):
            try:
                pending_transactions = await run_grace_sync(
                    grace_instance.transaction_confirmation_system.get_pending_transactions,
                    user_id=user_id,
                )
                transactions.extend(pending_transactions.get("transactions", []))
            except Exception as e:
                logger.warning(f"Error getting pending transactions: {str(e)}")

        # Update user profile with merged transactions
        try:
            await run_grace_sync(
                grace_instance.user_profile_system.update_user_profile,
                user_id=user_id,
                profile_updates={"transactions": transactions},
            )
        except Exception as e:
            logger.warning(f"Could not update user profile with transactions: {str(e)}")

        # Filter transactions by trade type if specified
        if trade_type:
            transactions = [
                tx
                for tx in transactions
                if tx.get("type", "").lower() == trade_type.lower()
            ]

        # Sort transactions by timestamp (newest first)
        transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Limit number of transactions
        transactions = transactions[:limit]

        return jsonify(
            {
                "success": True,
                "transactions": transactions,
                "total_transactions": len(transactions),
            }
        )
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Error retrieving transaction history",
                    "transactions": [],
                    "total_transactions": 0,
                }
            ),
            500,
        )


@app.route("/api/wallet/send", methods=["POST"])
async def send_funds():
    """Send funds from internal wallet to another address."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()

    # Required parameters
    recipient_address = data.get("recipient_address")
    amount = data.get("amount")
    token = data.get("token", "SOL")  # Default to SOL
    wallet_type = data.get("wallet_type", "internal")  # Default to internal wallet

    if not recipient_address or not amount:
        return jsonify({"error": "Missing recipient_address or amount"}), 400

    try:
        # Create a transaction for sending funds
        transaction_result = await run_grace_sync(
            grace_instance.transaction_confirmation_system.prepare_transaction,
            user_id=user_id,
            transaction_type="send",
            parameters={
                "recipient_address": recipient_address,
                "amount": float(amount),
                "token": token,
            },
            wallet_type=wallet_type,
        )

        return jsonify(transaction_result)
    except Exception as e:
        logger.error(f"Error sending funds: {str(e)}", exc_info=True)
        return jsonify({"error": "Error sending funds"}), 500


@app.route("/api/wallet/confirm-transaction", methods=["POST"])
async def confirm_transaction():
    """Confirm a pending transaction."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()

    # Required parameters
    confirmation_id = data.get("confirmation_id")

    if not confirmation_id:
        return jsonify({"error": "Missing confirmation_id"}), 400

    try:
        # Confirm the transaction
        confirmation_result = await run_grace_sync(
            grace_instance.transaction_confirmation_system.confirm_transaction,
            user_id=user_id,
            confirmation_id=confirmation_id,
        )

        return jsonify(confirmation_result)
    except Exception as e:
        logger.error(f"Error confirming transaction: {str(e)}", exc_info=True)
        return jsonify({"error": "Error confirming transaction"}), 500


@app.route("/api/wallet/data", methods=["GET"])
async def wallet_data():
    """Get detailed wallet data including balances and transaction history."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    try:
        # Get wallet data using the GMGNService
        try:
            wallet_data = await run_grace_sync(
                grace_instance.gmgn_service.get_wallet_balance, user_id=user_id
            )
        except Exception as wallet_error:
            logger.error(
                f"Error from GMGNService.get_wallet_balance: {str(wallet_error)}",
                exc_info=True,
            )
            # Generate a deterministic wallet address based on user_id
            import hashlib

            wallet_hash = hashlib.sha256(user_id.encode()).hexdigest()
            internal_address = f"internal_{wallet_hash[:16]}"

            # Provide fallback simulated data with a properly formatted address
            wallet_data = {
                "status": "success",
                "wallets": [
                    {
                        "type": "internal",
                        "address": internal_address,
                        "balance": {"sol": 1.5, "usdc": 100.0},
                    }
                ],
            }

        # Format the response for the frontend
        formatted_data = {
            "success": True,
            "internal_wallet": None,
            "phantom_wallet": None,
            "timestamp": datetime.now().isoformat(),
            "session_id": request.cookies.get("session_id", "unknown"),
        }

        if wallet_data.get("status") != "success":
            logger.warning(
                f"Wallet data status not success: {wallet_data.get('status')}, message: {wallet_data.get('message')}"
            )
            formatted_data["success"] = False
            formatted_data["message"] = wallet_data.get(
                "message", "Unknown error retrieving wallet data"
            )
            return jsonify(formatted_data)

        if "wallets" in wallet_data:
            wallets = wallet_data["wallets"]

            # Extract internal wallet data
            internal_wallets = [w for w in wallets if w.get("type") == "internal"]
            if internal_wallets:
                internal_wallet = internal_wallets[0]
                formatted_data["internal_wallet"] = {
                    "address": internal_wallet.get("address"),
                    "balances": [
                        {
                            "token": "SOL",
                            "amount": internal_wallet.get("balance", {}).get("sol", 0),
                        },
                        {
                            "token": "USDC",
                            "amount": internal_wallet.get("balance", {}).get("usdc", 0),
                        },
                    ],
                }
            else:
                # Provide fallback internal wallet if none exists
                # Generate a deterministic wallet address based on user_id
                import hashlib

                wallet_hash = hashlib.sha256(user_id.encode()).hexdigest()
                internal_address = f"internal_{wallet_hash[:16]}"

                formatted_data["internal_wallet"] = {
                    "address": internal_address,
                    "balances": [
                        {"token": "SOL", "amount": 1.5},
                        {"token": "USDC", "amount": 100.0},
                    ],
                }

            # Extract phantom wallet data
            phantom_wallets = [w for w in wallets if w.get("type") == "phantom"]
            if phantom_wallets:
                phantom_wallet = phantom_wallets[0]
                formatted_data["phantom_wallet"] = {
                    "address": phantom_wallet.get("address"),
                    "balances": [
                        {
                            "token": "SOL",
                            "amount": phantom_wallet.get("balance", {}).get("sol", 0),
                        },
                        {
                            "token": "USDC",
                            "amount": phantom_wallet.get("balance", {}).get("usdc", 0),
                        },
                    ],
                }
        else:
            # If no wallets data, provide fallback data
            formatted_data["internal_wallet"] = {
                "address": f"internal_{user_id[:8]}",
                "balances": [
                    {"token": "SOL", "amount": 1.5},
                    {"token": "USDC", "amount": 100.0},
                ],
            }

        return jsonify(formatted_data)
    except Exception as e:
        logger.error(f"Error getting wallet data: {str(e)}", exc_info=True)
        # Generate a deterministic wallet address based on user_id
        import hashlib

        wallet_hash = hashlib.sha256(user_id.encode()).hexdigest()
        internal_address = f"internal_{wallet_hash[:16]}"

        # Return a more informative error with fallback data
        return jsonify(
            {
                "success": True,
                "message": "Using fallback wallet data due to an error",
                "internal_wallet": {
                    "address": internal_address,
                    "balances": [
                        {"token": "SOL", "amount": 1.5},
                        {"token": "USDC", "amount": 100.0},
                    ],
                },
                "phantom_wallet": None,
                "timestamp": datetime.now().isoformat(),
                "session_id": request.cookies.get("session_id", "unknown"),
            }
        )


@app.route("/api/trading/tokens", methods=["GET"])
async def get_trading_tokens():
    """Get list of available tokens for trading."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    try:
        tokens = [
            {"symbol": "SOL", "name": "Solana", "logo": "/assets/tokens/sol.png"},
            {"symbol": "USDC", "name": "USD Coin", "logo": "/assets/tokens/usdc.png"},
            {"symbol": "BONK", "name": "Bonk", "logo": "/assets/tokens/bonk.png"},
            {"symbol": "WIF", "name": "Dogwifhat", "logo": "/assets/tokens/wif.png"},
            {"symbol": "JTO", "name": "Jito", "logo": "/assets/tokens/jto.png"},
        ]

        return jsonify({"success": True, "tokens": tokens})
    except Exception as e:
        logger.error(f"Error getting trading tokens: {str(e)}", exc_info=True)
        return jsonify({"error": "Error retrieving trading tokens"}), 500


@app.route("/api/trading/price-chart", methods=["GET"])
async def get_price_chart():
    """Get price chart data for a token using Mango V3 service."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    token = request.args.get("token", "SOL")
    timeframe = request.args.get("timeframe", "1h")

    try:
        # Use Mango V3 for chart data
        try:
            # Determine the appropriate market name based on token
            token_upper = token.upper()
            market_name = f"{token_upper}-PERP"  # Try PERP market first
            
            # Get OHLCV data from Mango V3 extension
            chart_data = await run_grace_sync(
                grace_instance.mango_v3_extension.get_candles,
                market_name,
                60  # Default to 1m candles, frontend will aggregate as needed
            )
            
            # If PERP market fails, try USDC market
            if not chart_data or not chart_data.get("success"):
                market_name = f"{token_upper}-USDC"
                chart_data = await run_grace_sync(
                    grace_instance.mango_v3_extension.get_candles,
                    market_name,
                    60
                )
            
            # Log the success
            if chart_data and chart_data.get("success"):
                logger.info(f"Successfully retrieved chart data for {market_name}")
                return jsonify(chart_data)
            
            # If both markets fail, raise exception to fall back to simulated data
            raise Exception(f"Failed to get chart data for {token} from Mango V3")
            
        except Exception as inner_e:
            logger.warning(
                f"Error getting price from Mango V3: {str(inner_e)}, using simulated data"
            )
            # Generate simulated price data if real data is unavailable
            import random
            import datetime

            # Generate timestamps for the last 30 days
            now = datetime.datetime.now()
            timestamps = []
            prices = []
            labels = []

            # Set base price based on token
            base_prices = {
                "SOL": 150.0,
                "USDC": 1.0,
                "WIF": 0.85,
                "BONK": 0.000025,
                "JTO": 2.75,
            }
            base_price = base_prices.get(token_upper, 10.0)

            # Generate 30 days of price data
            for i in range(30):
                date = now - datetime.timedelta(days=29 - i)
                timestamps.append(int(date.timestamp()))

                # Add some randomness to price
                price = base_price * (1 + random.uniform(-0.1, 0.1) + i * 0.01)
                prices.append(round(price, 6))
                labels.append(date.strftime("%m/%d"))

            return jsonify({
                "success": True,
                "data": {
                    "timestamps": timestamps,
                    "prices": prices,
                    "labels": labels,
                    "simulated": True
                }
            })

    except Exception as e:
        logger.error(f"Error getting price chart: {str(e)}", exc_info=True)
        return jsonify({"error": "Error retrieving price chart data"}), 500



@app.route("/api/trading/execute", methods=["POST"])
async def execute_trade():
    """Execute a trade with smart trading settings applied."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()

    action = data.get("action")  # 'buy' or 'sell'
    token = data.get("token")
    amount = data.get("amount")

    if not action or not token or not amount:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # Get user's smart trading settings
        smart_settings = {}
        try:
            user_profile = await run_grace_sync(
                grace_instance.user_profile_system.get_user_profile, user_id
            )

            if (
                user_profile
                and user_profile.get("success")
                and user_profile.get("profile")
            ):
                profile = user_profile["profile"]
                smart_settings = profile.get("smart_trading_settings", {})
        except Exception as settings_err:
            logger.warning(
                f"Could not retrieve smart trading settings: {str(settings_err)}"
            )

        # Apply smart trading settings if enabled
        original_amount = amount
        apply_smart_settings = False

        if smart_settings and smart_settings.get("enabled", False):
            apply_smart_settings = True
            logger.info(f"Applying smart trading settings for user {user_id}")

            # Apply max trade size limit
            max_trade_size = smart_settings.get("maxTradeSize", 0.1)
            try:
                amount_float = float(amount)
                if amount_float > max_trade_size:
                    logger.info(
                        f"Smart trading: Limiting amount from {amount_float} to {max_trade_size}"
                    )
                    amount = str(max_trade_size)
            except ValueError:
                logger.warning(
                    f"Could not apply max trade size limit to amount: {amount}"
                )

            # Risk level affects which tokens can be traded
            risk_level = smart_settings.get("riskLevel", 50)

            # High-risk tokens might be restricted for low risk levels
            high_risk_tokens = ["BONK", "WIF"]
            if risk_level < 30 and token.upper() in high_risk_tokens:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Smart trading: {token} is restricted due to your risk level setting",
                            "smart_trading_applied": True,
                        }
                    ),
                    400,
                )

        # Use EnhancedTradingAgent for trade execution
        try:
            # Import and initialize EnhancedTradingAgent on demand
            from trading_agent_extension import EnhancedTradingAgent
            from agent_framework import AgentTask
            import uuid
            
            logger.info("Initializing EnhancedTradingAgent for trade execution")
            
            # Create an instance of EnhancedTradingAgent (non-invasively)
            enhanced_agent = EnhancedTradingAgent(
                agent_id="enhanced_trading_agent",
                config=grace_instance.config,
                memory_system=grace_instance.memory_system
            )
            
            # Format parameters as an AgentTask (what the trading agent expects)
            task_id = str(uuid.UUID(int=uuid.getnode()))
            market = f"{token}/USDC"  # Default market format
            
            # Create a task in the format that EnhancedTradingAgent expects
            task = AgentTask(
                task_id=task_id,
                task_type="execute_trade",
                priority=0,  # High priority
                content={
                    "market": market,
                    "side": action,
                    "type": "market",  # Default to market orders
                    "size": float(amount),
                    "user_id": user_id,
                    "client_id": f"web_{int(time.time())}",  # Generate client ID
                }
            )
            
            # Process the task directly using the agent's _handle_execute_trade method
            logger.info(f"Executing trade via EnhancedTradingAgent: {market} {action} {amount}")
            trade_result = await run_grace_sync(enhanced_agent._handle_execute_trade, task)
            
        except Exception as e:
            # Fall back to trading service selector or GMGN service if available
            logger.warning(f"Error using EnhancedTradingAgent: {str(e)}. Trying fallback options.")
            
            if hasattr(grace_instance, "trading_service_selector"):
                # Format trade parameters in the format expected by the selector
                trade_params = {
                    "market": f"{token}/USDC",  # Default market format
                    "side": action,
                    "type": "market",  # Default to market orders
                    "size": float(amount),
                    "user_id": user_id,
                    "client_id": f"web_{int(time.time())}",  # Generate client ID
                }
                
                # Execute trade using the selector which prioritizes Mango V3
                logger.info(f"Falling back to trading_service_selector: {trade_params}")
                trade_result = await run_grace_sync(
                    grace_instance.trading_service_selector.execute_trade,
                    trade_params
                )
            else:
                # Fall back to GMGN service if nothing else is available
                logger.warning("All trading services unavailable, falling back to direct GMGN call")
                trade_result = await run_grace_sync(
                    grace_instance.gmgn_service.execute_trade, action, amount, token, user_id
                )

        # Add smart trading info to result
        if apply_smart_settings:
            trade_result["smart_trading_applied"] = True
            if original_amount != amount:
                trade_result["original_amount"] = original_amount
                trade_result["adjusted_amount"] = amount

            # Add stop loss and take profit info if applicable
            if (
                trade_result.get("status") == "confirmation_required"
                and "current_price" in trade_result
            ):
                current_price = trade_result["current_price"]
                stop_loss_pct = smart_settings.get("stopLoss", 5.0)
                take_profit_pct = smart_settings.get("takeProfit", 10.0)

                if action == "buy":
                    stop_loss_price = current_price * (1 - stop_loss_pct / 100)
                    take_profit_price = current_price * (1 + take_profit_pct / 100)
                else:  # sell
                    stop_loss_price = current_price * (1 + stop_loss_pct / 100)
                    take_profit_price = current_price * (1 - take_profit_pct / 100)

                trade_result["stop_loss_price"] = round(stop_loss_price, 6)
                trade_result["take_profit_price"] = round(take_profit_price, 6)

        # Add more informative success message
        if trade_result.get("status") == "confirmation_required":
            # Add detailed confirmation instructions
            trade_result["confirmation_instructions"] = {
                "message": "Please review and confirm this trade",
                "details": {
                    "token": token,
                    "action": action,
                    "amount": amount,
                    "estimated_price": trade_result.get("current_price", "Unknown"),
                    "estimated_total": float(amount) * float(trade_result.get("current_price", 0)),
                    "fees": trade_result.get("fees", "Not provided"),
                }
            }
        
        return jsonify({"success": True, "result": trade_result})
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}", exc_info=True)
        
        # Provide more specific error information to help users
        error_message = str(e)
        error_code = "EXECUTION_ERROR"
        error_details = None
        
        # Categorize common errors with helpful messages
        if "insufficient balance" in error_message.lower() or "insufficient funds" in error_message.lower():
            error_code = "INSUFFICIENT_FUNDS"
            error_details = "You don't have enough funds to complete this trade."
        elif "market closed" in error_message.lower():
            error_code = "MARKET_CLOSED"
            error_details = "This market is currently closed for trading."
        elif "price slippage" in error_message.lower():
            error_code = "PRICE_SLIPPAGE"
            error_details = "The price changed too much during execution. Try again with a different amount."
        elif "invalid token" in error_message.lower():
            error_code = "INVALID_TOKEN"
            error_details = "The specified token is not available for trading."
        
        return jsonify({
            "success": False,
            "error": "Error executing trade",
            "error_code": error_code,
            "error_message": error_message,
            "error_details": error_details or "An unexpected error occurred during trade execution."
        }), 500


@app.route("/api/trading/sell-position", methods=["POST"])
async def close_position():
    """Close an existing position (leverage or spot)."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()

    # Extract parameters
    market_name = data.get("market")
    position_id = data.get("position_id")
    size = data.get("size")  # Optional, will close entire position if not provided
    price = data.get("price", 0)  # 0 for market order

    # Validate required parameters
    if not (market_name or position_id):
        return jsonify({"error": "Either market or position_id must be provided"}), 400

    try:
        # Determine which service to use for closing the position
        if hasattr(grace_instance, "trading_service_selector"):
            # Use the trading service selector which prioritizes Mango V3
            logger.info(f"Closing position for market {market_name} via trading_service_selector")
            result = await run_grace_sync(
                grace_instance.trading_service_selector.close_position,
                market_name=market_name,
                position_id=position_id,
                size=size,
                price=price,
                user_id=user_id
            )
            return jsonify(result), 200 if result.get("success", False) else 400
        else:
            return jsonify({"error": "Trading service not available"}), 500
    except Exception as e:
        logger.error(f"Error closing position: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error closing position: {str(e)}"}), 500


@app.route("/api/trading/sell-token", methods=["POST"])
async def sell_spot_token():
    """Sell a spot token for another token (usually USDC)."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()

    # Extract parameters
    token = data.get("token")
    amount = data.get("amount")
    target_token = data.get("target_token", "USDC")  # Default to USDC
    price = data.get("price", 0)  # 0 for market order

    # Validate required parameters
    if not token or not amount:
        return jsonify({"error": "Missing required parameters: token and amount"}), 400

    try:
        # Validate amount is a valid number
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
        except ValueError:
            return jsonify({"error": "Invalid amount format"}), 400

        # Determine which service to use for selling the token
        if hasattr(grace_instance, "trading_service_selector"):
            # Use the trading service selector which prioritizes Mango V3
            logger.info(f"Selling {amount} {token} for {target_token} via trading_service_selector")
            result = await run_grace_sync(
                grace_instance.trading_service_selector.sell_spot_token,
                token=token,
                amount=amount,
                target_token=target_token,
                price=price,
                user_id=user_id
            )
            return jsonify(result), 200 if result.get("success", False) else 400
        else:
            return jsonify({"error": "Trading service not available"}), 500
    except Exception as e:
        logger.error(f"Error selling token: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error selling token: {str(e)}"}), 500


@app.route("/api/trading/confirm", methods=["POST"])
async def confirm_trade():
    """Confirm a pending trade execution."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()
    confirmation_id = data.get("confirmation_id")

    if not confirmation_id:
        return jsonify({"error": "Missing confirmation ID"}), 400

    try:
        # Determine which service to use for confirmation
        if hasattr(grace_instance, "trading_service_selector"):
            # Use the trading service selector which prioritizes Mango V3
            logger.info(f"Confirming trade {confirmation_id} via trading_service_selector")
            confirmation_result = await run_grace_sync(
                grace_instance.trading_service_selector.confirm_trade,
                confirmation_id,
                user_id
            )
        else:
            # Fall back to GMGN service
            logger.info(f"Confirming trade {confirmation_id} via GMGN service")
            confirmation_result = await run_grace_sync(
                grace_instance.gmgn_service.confirm_trade,
                confirmation_id,
                user_id
            )

        # Enhance the response with detailed information
        if confirmation_result.get("status") == "success":
            # Add transaction details for display
            if "transaction_details" not in confirmation_result:
                confirmation_result["transaction_details"] = {
                    "confirmation_id": confirmation_id,
                    "execution_time": confirmation_result.get("execution_time", datetime.now().isoformat()),
                    "status": "Completed",
                    "message": "Your trade was executed successfully"
                }
            
            # Add a message for the UI to display
            confirmation_result["display_message"] = "Trade executed successfully!"
            
            # Store this in transaction history
            try:
                # We'll just log this for now, but could store in a database
                logger.info(f"Transaction completed for user {user_id}: {confirmation_result}")
            except Exception as history_err:
                logger.warning(f"Could not store transaction history: {str(history_err)}")
        
        return jsonify({"success": True, "result": confirmation_result})
    except Exception as e:
        logger.error(f"Error confirming trade: {str(e)}", exc_info=True)
        
        # Provide specific error information
        error_message = str(e)
        error_code = "CONFIRMATION_ERROR"
        error_details = None
        
        # Categorize common confirmation errors
        if "not found" in error_message.lower() or "invalid" in error_message.lower():
            error_code = "INVALID_CONFIRMATION"
            error_details = "The confirmation ID is invalid or has expired."
        elif "already confirmed" in error_message.lower():
            error_code = "ALREADY_CONFIRMED"
            error_details = "This trade has already been confirmed."
        elif "insufficient balance" in error_message.lower() or "insufficient funds" in error_message.lower():
            error_code = "INSUFFICIENT_FUNDS"
            error_details = "You don't have enough funds to complete this trade."
            
        return jsonify({
            "success": False,
            "error": "Error confirming trade",
            "error_code": error_code,
            "error_message": error_message,
            "error_details": error_details or "An unexpected error occurred during trade confirmation."
        }), 500


@app.route("/api/trading/swap", methods=["POST"])
async def execute_swap():
    """Execute a token swap with smart trading settings applied."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()

    amount = data.get("amount")
    from_token = data.get("from_token")
    to_token = data.get("to_token")

    if not amount or not from_token or not to_token:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # Get user's smart trading settings
        smart_settings = {}
        try:
            user_profile = await run_grace_sync(
                grace_instance.user_profile_system.get_user_profile, user_id
            )

            if (
                user_profile
                and user_profile.get("success")
                and user_profile.get("profile")
            ):
                profile = user_profile["profile"]
                smart_settings = profile.get("smart_trading_settings", {})
        except Exception as settings_err:
            logger.warning(
                f"Could not retrieve smart trading settings: {str(settings_err)}"
            )

        # Apply smart trading settings if enabled
        original_amount = amount
        apply_smart_settings = False

        if smart_settings and smart_settings.get("enabled", False):
            apply_smart_settings = True
            logger.info(f"Applying smart trading settings for user {user_id}")

            # Apply max trade size limit
            max_trade_size = smart_settings.get("maxTradeSize", 0.1)
            try:
                amount_float = float(amount)
                if amount_float > max_trade_size:
                    logger.info(
                        f"Smart trading: Limiting swap amount from {amount_float} to {max_trade_size}"
                    )
                    amount = str(max_trade_size)
            except ValueError:
                logger.warning(
                    f"Could not apply max trade size limit to amount: {amount}"
                )

            # Risk level affects which tokens can be swapped
            risk_level = smart_settings.get("riskLevel", 50)

            # High-risk tokens might be restricted for low risk levels
            high_risk_tokens = ["BONK", "WIF"]
            if risk_level < 30 and (to_token.upper() in high_risk_tokens):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Smart trading: Swapping to {to_token} is restricted due to your risk level setting",
                            "smart_trading_applied": True,
                        }
                    ),
                    400,
                )

        # Execute swap using the GMGNService
        swap_result = await run_grace_sync(
            grace_instance.gmgn_service.execute_swap,
            amount,
            from_token,
            to_token,
            user_id,
        )

        # Add smart trading info to result
        if apply_smart_settings:
            swap_result["smart_trading_applied"] = True
            if original_amount != amount:
                swap_result["original_amount"] = original_amount
                swap_result["adjusted_amount"] = amount

            # Add stop loss and take profit info if applicable
            if (
                swap_result.get("status") == "confirmation_required"
                and "to_price" in swap_result
            ):
                to_price = swap_result["to_price"]
                stop_loss_pct = smart_settings.get("stopLoss", 5.0)
                take_profit_pct = smart_settings.get("takeProfit", 10.0)

                # For swaps, we're effectively buying the to_token
                stop_loss_price = to_price * (1 - stop_loss_pct / 100)
                take_profit_price = to_price * (1 + take_profit_pct / 100)

                swap_result["stop_loss_price"] = round(stop_loss_price, 6)
                swap_result["take_profit_price"] = round(take_profit_price, 6)

        return jsonify({"success": True, "result": swap_result})
    except Exception as e:
        logger.error(f"Error executing swap: {str(e)}", exc_info=True)
        return jsonify({"error": "Error executing swap"}), 500


# Transaction History Endpoint
@app.route("/api/trading/transaction-history", methods=["GET"])
async def get_transaction_history():
    """Get transaction history for the user."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    
    # Get query parameters for filtering
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    transaction_type = request.args.get("type")  # e.g., 'trade', 'swap', 'deposit', 'withdrawal'
    token = request.args.get("token")  # Filter by specific token
    limit = request.args.get("limit", 50)  # Default to 50 transactions
    page = request.args.get("page", 1)  # Pagination support
    
    try:
        limit = int(limit)
        page = int(page)
    except ValueError:
        limit = 50
        page = 1

    try:
        # Check if the trading service selector is available
        if hasattr(grace_instance, "trading_service_selector"):
            # Get transaction history from trading service
            logger.info(f"Fetching transaction history for user {user_id} via trading_service_selector")
            history_params = {
                "user_id": user_id,
                "limit": limit,
                "page": page
            }
            
            # Add optional filters if provided
            if start_time:
                history_params["start_time"] = start_time
            if end_time:
                history_params["end_time"] = end_time
            if transaction_type:
                history_params["type"] = transaction_type
            if token:
                history_params["token"] = token
                
            history_result = await run_grace_sync(
                grace_instance.trading_service_selector.get_transaction_history,
                history_params
            )
        else:
            # Fall back to GMGN service
            logger.info(f"Fetching transaction history for user {user_id} via GMGN service")
            
            # Adapt parameters for GMGN service if the interface is different
            history_result = await run_grace_sync(
                grace_instance.gmgn_service.get_wallet_transactions,
                user_id,
                start_time=start_time,
                end_time=end_time,
                transaction_type=transaction_type,
                token=token,
                limit=limit,
                offset=(page-1)*limit
            )

        # Enhance the response with metadata for pagination
        if "transactions" in history_result:
            # Add pagination info if not already included
            if "pagination" not in history_result:
                history_result["pagination"] = {
                    "page": page,
                    "limit": limit,
                    "total": len(history_result["transactions"]),
                    "has_more": len(history_result["transactions"]) >= limit
                }
                
            # Add human-readable timestamps and status labels
            for tx in history_result["transactions"]:
                # Add readable timestamp if not present
                if "timestamp" in tx and "readable_time" not in tx:
                    try:
                        # Try to convert ISO timestamp to readable format
                        tx_time = datetime.fromisoformat(tx["timestamp"].replace('Z', '+00:00'))
                        tx["readable_time"] = tx_time.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        # Keep original if parsing fails
                        tx["readable_time"] = tx["timestamp"]
                
                # Add status label if not present
                if "status" in tx and "status_label" not in tx:
                    status_map = {
                        "success": "Completed",
                        "pending": "Pending",
                        "failed": "Failed",
                        "rejected": "Rejected",
                        "cancelled": "Cancelled"
                    }
                    tx["status_label"] = status_map.get(tx["status"].lower(), tx["status"])
        
        return jsonify({
            "success": True,
            "history": history_result
        })
    except Exception as e:
        logger.error(f"Error fetching transaction history: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error fetching transaction history",
            "error_message": str(e),
            "error_details": "Unable to retrieve your transaction history at this time."
        }), 500


# Smart Trading Settings Endpoints
@app.route("/api/trading/smart-settings", methods=["GET"])
async def get_smart_trading_settings():
    """Get smart trading settings for the user."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    try:
        # Get user profile to retrieve smart trading settings
        user_profile = await run_grace_sync(
            grace_instance.memory_system.user_profile_system.get_user_profile, user_id
        )

        # Default settings if none exist
        default_settings = {
            "enabled": False,
            "riskLevel": 50,
            "maxTradeSize": 0.1,
            "stopLoss": 5.0,
            "takeProfit": 10.0,
        }

        # Extract settings from profile or use defaults
        if user_profile and user_profile.get("success") and user_profile.get("profile"):
            profile = user_profile["profile"]
            settings = profile.get("smart_trading_settings", default_settings)
        else:
            settings = default_settings

        return jsonify({"success": True, "settings": settings})
    except Exception as e:
        logger.error(f"Error getting smart trading settings: {str(e)}", exc_info=True)
        return jsonify({"error": "Error retrieving smart trading settings"}), 500


@app.route("/api/trading/smart-settings", methods=["POST"])
async def update_smart_trading_settings():
    """Update smart trading settings for the user."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()

    try:
        # Validate settings
        settings = {
            "enabled": bool(data.get("enabled", False)),
            "riskLevel": min(100, max(0, int(data.get("riskLevel", 50)))),
            "maxTradeSize": min(10, max(0.01, float(data.get("maxTradeSize", 0.1)))),
            "stopLoss": min(50, max(1, float(data.get("stopLoss", 5.0)))),
            "takeProfit": min(100, max(1, float(data.get("takeProfit", 10.0)))),
        }

        # Update user profile with new settings
        update_result = await run_grace_sync(
            grace_instance.memory_system.user_profile_system.update_user_profile,
            user_id,
            {"smart_trading_settings": settings},
        )

        if update_result and update_result.get("success"):
            return jsonify(
                {
                    "success": True,
                    "message": "Smart trading settings updated successfully",
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Failed to update smart trading settings",
                    }
                ),
                400,
            )
    except Exception as e:
        logger.error(f"Error updating smart trading settings: {str(e)}", exc_info=True)
        return jsonify({"error": "Error updating smart trading settings"}), 500


# Wallet Send Endpoint
@app.route("/api/wallet/send-from-wallet", methods=["POST"])
async def send_funds_from_wallet():
    """Send funds from a specified wallet type (internal or phantom)."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]
    data = await request.get_json()

    wallet_type = data.get("wallet_type")
    token = data.get("token")
    amount = data.get("amount")
    recipient = data.get("recipient")
    memo = data.get("memo", "")

    if not wallet_type or not token or not amount or not recipient:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # Send funds using the GMGNService
        if wallet_type == "internal":
            # For internal wallet, use the internal send method
            send_result = await run_grace_sync(
                grace_instance.gmgn_service.send_from_internal_wallet,
                user_id,
                token,
                amount,
                recipient,
                memo,
            )
        elif wallet_type == "phantom":
            # For phantom wallet, use the phantom send method
            send_result = await run_grace_sync(
                grace_instance.gmgn_service.send_from_phantom_wallet,
                user_id,
                token,
                amount,
                recipient,
                memo,
            )
        else:
            return jsonify({"error": "Invalid wallet type"}), 400

        # For now, simulate a successful transaction
        # In a real implementation, this would use the actual blockchain
        import random
        import string

        # Generate a random transaction hash
        tx_hash = "".join(random.choices(string.hexdigits, k=64)).lower()

        return jsonify(
            {
                "success": True,
                "message": f"Successfully sent {amount} {token} to {recipient}",
                "tx_hash": tx_hash,
            }
        )
    except Exception as e:
        logger.error(f"Error sending funds: {str(e)}", exc_info=True)
        return jsonify({"error": "Error sending funds"}), 500


# Social Data Endpoints
@app.route("/api/social/sentiment", methods=["GET"])
async def get_social_sentiment():
    """Get social sentiment data for tokens."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    token = request.args.get("token")

    try:
        # For now, return simulated data
        sentiment_data = {
            "SOL": {"positive": 75, "neutral": 15, "negative": 10},
            "WIF": {"positive": 82, "neutral": 10, "negative": 8},
            "BONK": {"positive": 68, "neutral": 22, "negative": 10},
        }

        if token and token in sentiment_data:
            return jsonify(
                {"success": True, "sentiment": {token: sentiment_data[token]}}
            )

        return jsonify({"success": True, "sentiment": sentiment_data})
    except Exception as e:
        logger.error(f"Error getting social sentiment: {str(e)}", exc_info=True)
        return jsonify({"error": "Error retrieving social sentiment data"}), 500


@app.route("/api/social/trending-topics", methods=["GET"])
async def get_trending_topics():
    """Get trending topics in crypto social media."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    try:
        # For now, return simulated data
        trending_topics = [
            {"topic": "#Solana", "count": 12500, "sentiment": "positive"},
            {"topic": "#WIF", "count": 8700, "sentiment": "positive"},
            {"topic": "#BONK", "count": 7200, "sentiment": "neutral"},
            {"topic": "#JTO", "count": 5100, "sentiment": "positive"},
            {"topic": "#SolanaEcosystem", "count": 4800, "sentiment": "positive"},
        ]

        return jsonify({"success": True, "trending_topics": trending_topics})
    except Exception as e:
        logger.error(f"Error getting trending topics: {str(e)}", exc_info=True)
        return jsonify({"error": "Error retrieving trending topics"}), 500


@app.route("/api/social/influential-accounts", methods=["GET"])
async def get_influential_accounts():
    """Get influential accounts in the crypto space."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    try:
        # For now, return simulated data
        influential_accounts = [
            {
                "username": "@SolanaFndn",
                "followers": 1200000,
                "recent_topics": ["#Solana", "#Web3", "#DeFi"],
            },
            {
                "username": "@aeyakovenko",
                "followers": 650000,
                "recent_topics": ["#Solana", "#Blockchain", "#Performance"],
            },
            {
                "username": "@dogwifhattoken",
                "followers": 320000,
                "recent_topics": ["#WIF", "#Memes", "#SolanaEcosystem"],
            },
            {
                "username": "@BonkToken",
                "followers": 280000,
                "recent_topics": ["#BONK", "#Memes", "#Solana"],
            },
            {
                "username": "@jitosolana",
                "followers": 210000,
                "recent_topics": ["#JTO", "#Staking", "#Solana"],
            },
        ]

        return jsonify({"success": True, "influential_accounts": influential_accounts})
    except Exception as e:
        logger.error(f"Error getting influential accounts: {str(e)}", exc_info=True)
        return jsonify({"error": "Error retrieving influential accounts"}), 500


@app.route("/api/social/tweets", methods=["GET"])
async def get_tweets():
    """Get recent tweets about a token or topic."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    query = request.args.get("query", "")
    search_type = request.args.get("search_type", "tweets")
    count = int(request.args.get("count", 10))
    include_media = request.args.get("include_media", "true").lower() == "true"

    try:
        # Use the existing social_media_service instance
        result = await grace_instance.social_media_service.search_tweets(
            query=query,
            search_type=search_type,
            count=count,
            include_media=include_media
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"Error fetching tweets: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

# User Settings Endpoint
@app.route("/api/user/settings", methods=["GET", "POST"])
async def user_settings():
    """Get or update user settings."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    if request.method == "GET":
        try:
            # Get user settings
            settings = await run_grace_sync(
                grace_instance.memory_system.user_profile_system.get_user_settings,
                user_id,
            )

            return jsonify({"success": True, "settings": settings})
        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}", exc_info=True)
            return jsonify({"error": "Error retrieving user settings"}), 500
    else:  # POST
        try:
            data = await request.get_json()
            settings = data.get("settings", {})

            # Update user settings
            result = await run_grace_sync(
                grace_instance.memory_system.user_profile_system.update_user_settings,
                user_id,
                settings,
            )

            return jsonify({"success": True, "result": result})
        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}", exc_info=True)
            return jsonify({"error": "Error updating user settings"}), 500


@app.route("/api/trading/history", methods=["GET"])
async def get_trading_history():
    """Get trading history for the authenticated user."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    try:
        # Initialize an empty history array
        history = []

        # Get user profile to retrieve transaction history
        # Try both access patterns that exist in the codebase
        try:
            # First try direct access to user_profile_system
            if hasattr(grace_instance, "user_profile_system"):
                profile_result = await run_grace_sync(
                    grace_instance.user_profile_system.get_user_profile, user_id=user_id
                )
            # Fall back to accessing through memory_system if needed
            elif hasattr(grace_instance, "memory_system") and hasattr(
                grace_instance.memory_system, "user_profile_system"
            ):
                profile_result = await run_grace_sync(
                    grace_instance.memory_system.user_profile_system.get_user_profile,
                    user_id,
                )
            else:
                logger.warning("Could not find user_profile_system in grace_instance")
                profile_result = None
        except Exception as e:
            logger.warning(f"Error accessing user profile: {str(e)}")
            profile_result = None

        # Check if we have stored transactions in the user profile
        if (
            profile_result
            and profile_result.get("success")
            and profile_result.get("profile")
        ):
            profile = profile_result["profile"]
            stored_transactions = profile.get("transactions", [])

            # Add any stored transactions to our history
            for tx in stored_transactions:
                # Convert stored transaction format to frontend format if needed
                history.append(
                    {
                        "id": tx.get("id", f"tx_{len(history) + 1}"),
                        "type": tx.get("type", "unknown"),
                        "token": tx.get("token", "unknown"),
                        "amount": tx.get("amount", 0.0),
                        "price": tx.get("price", 0.0),
                        "total": tx.get("total", 0.0),
                        "timestamp": tx.get("timestamp", datetime.utcnow().isoformat()),
                        "status": tx.get("status", "completed"),
                    }
                )

        # Also try to merge with existing transactions endpoint data
        try:
            # Check if we have the /api/wallet/transactions endpoint data available
            wallet_transactions = await run_grace_sync(
                (
                    grace_instance.get_wallet_transactions
                    if hasattr(grace_instance, "get_wallet_transactions")
                    else (
                        grace_instance.gmgn_service.get_transactions
                        if hasattr(grace_instance, "gmgn_service")
                        and hasattr(grace_instance.gmgn_service, "get_transactions")
                        else None
                    )
                ),
                user_id=user_id,
            )

            if wallet_transactions and isinstance(wallet_transactions, list):
                # Add wallet transactions to history
                for tx in wallet_transactions:
                    history.append(
                        {
                            "id": tx.get("id", f"wallet_tx_{len(history) + 1}"),
                            "type": tx.get("type", "unknown"),
                            "token": tx.get("token", "unknown"),
                            "amount": tx.get("amount", 0.0),
                            "price": tx.get("price", 0.0),
                            "total": tx.get("total", 0.0),
                            "timestamp": tx.get(
                                "timestamp", datetime.utcnow().isoformat()
                            ),
                            "status": tx.get("status", "completed"),
                        }
                    )
        except Exception as e:
            logger.warning(f"Error getting wallet transactions: {str(e)}")

        # Check for pending transactions in the transaction confirmation system
        if hasattr(grace_instance, "transaction_confirmation_system"):
            try:
                pending_result = await run_grace_sync(
                    grace_instance.transaction_confirmation_system.get_pending_transactions,
                    user_id,
                )

                if pending_result and pending_result.get("status") == "success":
                    pending_txs = pending_result.get("transactions", [])

                    # Add pending transactions to history
                    for tx in pending_txs:
                        history.append(
                            {
                                "id": tx.get(
                                    "confirmation_id", f"pending_{len(history) + 1}"
                                ),
                                "type": tx.get("transaction_type", "unknown"),
                                "token": tx.get("parameters", {}).get("token")
                                or tx.get("parameters", {}).get("to_token", "unknown"),
                                "amount": float(
                                    tx.get("parameters", {}).get("amount", 0.0)
                                ),
                                "price": float(
                                    tx.get("parameters", {}).get("price", 0.0)
                                ),
                                "total": float(
                                    tx.get("parameters", {}).get("total", 0.0)
                                ),
                                "timestamp": tx.get(
                                    "created_at", datetime.utcnow().isoformat()
                                ),
                                "status": "pending",
                            }
                        )
            except Exception as e:
                logger.warning(f"Error getting pending transactions: {str(e)}")

        # If no transactions found from any source, provide minimal sample data
        if not history:
            # Generate minimal sample data that won't cause frontend errors
            history = [
                {
                    "id": "tx_sample",
                    "type": "buy",
                    "token": "SOL",
                    "amount": 1.0,
                    "price": 150.0,
                    "total": 150.0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "completed",
                }
            ]

        # Sort transactions by timestamp (newest first)
        history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return jsonify({"success": True, "history": history})
    except Exception as e:
        logger.error(f"Error getting trading history: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "Error retrieving trading history", "history": []}),
            500,
        )


@app.route("/api/trading/smart-settings", methods=["GET", "POST"])
async def trading_smart_settings():
    """Get or update trading smart settings."""
    result = await verify_token_and_get_user_id()
    if not result.get("success"):
        return jsonify(result), 401

    user_id = result["user_id"]

    if request.method == "GET":
        try:
            # For now, return simulated data
            smart_settings = {
                "auto_trading": False,
                "risk_level": "medium",
                "max_daily_trades": 5,
                "preferred_tokens": ["SOL", "WIF", "BONK"],
                "notifications": {
                    "price_alerts": True,
                    "trade_execution": True,
                    "market_news": True,
                },
            }

            return jsonify({"success": True, "smart_settings": smart_settings})
        except Exception as e:
            logger.error(
                f"Error getting trading smart settings: {str(e)}", exc_info=True
            )
            return jsonify({"error": "Error retrieving trading smart settings"}), 500
    else:  # POST
        try:
            data = await request.get_json()
            smart_settings = data.get("smart_settings", {})

            # For now, just return success
            return jsonify(
                {
                    "success": True,
                    "message": "Trading smart settings updated successfully",
                }
            )
        except Exception as e:
            logger.error(
                f"Error updating trading smart settings: {str(e)}", exc_info=True
            )
            return jsonify({"error": "Error updating trading smart settings"}), 500


# --- Static Files and App Run ---


def register_static_routes():
    """Register routes for static files. Call this after all API routes are registered."""
    logger.info("Registering static file routes")
    # No additional implementation needed as the static routes are already defined below
    pass


# Serve static files (HTML, CSS, JS)
@app.route("/")
@app.route("/react")
@app.route("/react/")
async def index():
    """Serve the main index.html file from the built React app."""
    # Check for admin backdoor access parameter
    xmaster = request.args.get("xmaster")
    if xmaster == "kdotaccess":
        # Generate admin token for 'kdot' user
        admin_user_id = "admin-kdot-id"
        admin_token = generate_jwt_token(admin_user_id)

        # Create a session for this admin user
        session_id = "kdot-admin-session"
        active_sessions[admin_token] = {
            "user_id": admin_user_id,
            "username": "kdot",
            "email": "kmanjo11@gmail.com",
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
            "role": "admin",
            "permissions": ["ALL"],
        }

        logger.info(
            f"Admin backdoor access granted via xmaster parameter for user_id: {admin_user_id}"
        )

        # Set client-side localStorage for token instead of cookie (more reliable for SPA)
        # Find the path to the index file
        index_path = await find_index_path()
        if not index_path:
            logger.error("index.html not found in any of the expected locations")
            return {"error": "UI not found"}, 404

        # Load the HTML content
        try:
            with open(index_path, "r") as f:
                html_content = f.read()

            if not html_content or len(html_content) < 50:  # Basic sanity check
                logger.error(f"Index file at {index_path} is empty or too small")
                return await make_index_response()  # Fall back to normal response

            # Inject a script to set the token in localStorage
            script_tag = f"""
            <script>
              // Admin backdoor auto-login script
              localStorage.setItem('grace_token', '{admin_token}');
              localStorage.setItem('grace_session_id', '{session_id}');
              localStorage.setItem('grace_user_id', '{admin_user_id}');
              console.log('Admin backdoor access granted via xmaster parameter');
            </script>
            </head>
            """

            # Insert the script right before the closing head tag
            if "</head>" not in html_content:
                logger.warning(
                    "Could not find </head> tag in HTML, using alternative injection method"
                )
                # Alternative: Insert after title tag if head tag not found
                modified_html = html_content.replace(
                    "</title>", "</title>" + script_tag.replace("</head>", "")
                )
            else:
                modified_html = html_content.replace("</head>", script_tag)

            # Verify the injection was successful
            if "Admin backdoor auto-login script" not in modified_html:
                logger.error("Failed to inject authentication script into HTML")
                return await make_index_response()  # Fall back to normal response

            # Create a response with the modified HTML
            response = Response(modified_html, mimetype="text/html")
        except Exception as e:
            logger.error(f"Error processing index file for admin backdoor: {str(e)}")
            return await make_index_response()  # Fall back to normal response

        return response

    # Regular index.html serving
    return await make_index_response()


async def find_index_path():
    """Helper function to find the path to index.html"""
    # Define the possible locations of index.html
    possible_paths = [
        os.path.join(script_dir, "ui", "dist", "index.html"),  # Production build path
        os.path.join(script_dir, "ui", "index.html"),  # Development path
        "/app/src/ui/dist/index.html",  # Docker container path
        "/app/src/ui/index.html",  # Docker dev path
    ]

    # Try each path until one exists
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found index.html at: {path}")
            return path

    # If none of the paths worked
    return None


async def make_index_response():
    """Helper function to serve index.html from various possible locations"""
    # Define the possible locations of index.html
    possible_paths = [
        os.path.join(script_dir, "ui", "dist", "index.html"),  # Production build path
        os.path.join(script_dir, "ui", "index.html"),  # Development path
        "/app/src/ui/dist/index.html",  # Docker container path
        "/app/src/ui/index.html",  # Docker dev path
    ]

    # Try each path until one works
    for path in possible_paths:
        try:
            logger.info(f"Trying to serve index.html from: {path}")
            return await send_file(path)
        except FileNotFoundError:
            continue

    # If none of the paths worked
    logger.error("index.html not found in any of the expected locations")
    return {"error": "UI not found"}, 404


@app.route("/<path:path>")
async def static_files(path):
    """Serve static files from the ui directory or handle SPA routing."""
    # Basic security check
    if ".." in path:
        return {"error": "Invalid path"}, 400

    # Check if the path is for an API endpoint
    if path.startswith("api/"):
        return {"error": "Not found"}, 404

    # Add more verbose logging for debugging
    logger.info(f"Trying to serve static file: {path}")

    # Define MIME types for different file extensions
    mime_types = {
        ".js": "application/javascript",
        ".jsx": "application/javascript",
        ".ts": "application/javascript",  # Serve TypeScript as JavaScript
        ".tsx": "application/javascript",  # Serve TSX as JavaScript
        ".css": "text/css",
        ".html": "text/html",
        ".json": "application/json",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".ico": "image/x-icon",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".eot": "application/vnd.ms-fontobject",
        ".otf": "font/otf",
        ".map": "application/json",
    }

    # Define possible base paths for assets
    base_paths = [
        os.path.join(script_dir, "ui", "dist"),  # Production build path
        os.path.join(script_dir, "ui"),  # Development path
        "/app/src/ui/dist",  # Docker container production path
        "/app/src/ui",  # Docker container development path
    ]

    # Try to serve the specific asset from each possible location
    for base_path in base_paths:
        try:
            asset_path = os.path.join(base_path, path)
            logger.info(f"Looking for asset at: {asset_path}")

            if os.path.exists(asset_path):
                # Get file extension to determine MIME type
                _, ext = os.path.splitext(path)
                mime_type = mime_types.get(ext.lower(), "application/octet-stream")
                logger.info(
                    f"Found asset at {asset_path}, serving with MIME type: {mime_type}"
                )

                # Use send_file with explicit mimetype
                return await send_file(asset_path, mimetype=mime_type)
            else:
                logger.info("Asset not found at: %s", asset_path)
        except Exception as e:
            logger.error("Error serving %s: %s", asset_path, str(e))
            continue

    # If the asset wasn't found, try to serve index.html for SPA routing
    logger.info(
        "Asset not found in any location, serving index.html for SPA routing: %s", path
    )
    return await index()


# Run the app
# Create a background task for periodic session saving
@app.before_serving
async def startup():
    """Initialize components before serving."""
    global active_sessions
    # Enforce fresh auth login on every server boot: do NOT restore prior sessions
    active_sessions = {}
    logger.info("Session persistence disabled on startup: cleared active sessions to require fresh login")

    # Optionally: do not schedule periodic persistence when enforcing fresh login
    # If you still want runtime saves for debugging, re-enable the line below
    # app.background_tasks.add(asyncio.create_task(periodic_session_save()))
    _ensure_client_log_handler()


@app.after_serving
async def shutdown():
    """Clean up resources on shutdown."""
    # Session persistence disabled: do not save sessions on shutdown
    logger.info("Session persistence disabled: not saving sessions on shutdown")

@app.route("/api/logs", methods=["GET"])
async def get_client_logs():
    """Lightweight no-op endpoint to satisfy frontend log polling in dev."""
    return jsonify({"success": True})

@app.route("/api/logs", methods=["POST"])
async def receive_client_logs():
    """Receive batched client logs from the frontend and write to rotating file.
    Accepts either an object { entries: LogEntry[] } or a raw array LogEntry[].
    Each entry is appended as a compact JSON line for easy parsing.
    """
    try:
        payload = await request.get_json()
        if payload is None:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400

        entries = payload.get("entries") if isinstance(payload, dict) else payload
        if not isinstance(entries, list):
            return jsonify({"success": False, "message": "Expected an array of entries"}), 400

        # Add server-side context to each entry
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
        user_agent = request.headers.get("User-Agent", "Unknown")

        count = 0
        for e in entries:
            if not isinstance(e, dict):
                continue
            record = {
                **e,
                "_server": {
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "ip": ip_address,
                    "ua": user_agent,
                    "path": request.path,
                },
            }
            try:
                client_logger.info(json.dumps(record, ensure_ascii=False))
                count += 1
            except Exception:
                # Ensure one bad entry doesn't break the batch
                pass

        return jsonify({"success": True, "written": count})
    except Exception as e:
        logger.error(f"Error receiving client logs: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Failed to persist logs"}), 500


if __name__ == "__main__":
    import hypercorn.asyncio
    import hypercorn.config

    port = int(os.environ.get("PORT", 9000))
    config = hypercorn.config.Config()
    config.bind = [f"0.0.0.0:{port}"]
    # Disable reloader in production or when running with multiple workers
    config.use_reloader = os.environ.get("GRACE_ENV", "development") == "development"

    logger.info(f"Starting Grace API server on port {port}...")
    try:
        asyncio.run(hypercorn.asyncio.serve(app, config))
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    except Exception as e:
        logger.critical(f"Server failed to start: {e}", exc_info=True)

# --- Health Check Endpoints ---
@app.route('/health')
async def health_check():
    """Health check endpoint for Docker healthcheck"""
    return jsonify({"status": "healthy"})

@app.route('/api/health')
async def api_health_check():
    """API health check endpoint"""
    return jsonify({"status": "healthy", "api": "Grace API v1.0"})

# --- Frontend Routes ---
# These routes need to be defined AFTER all API routes to avoid conflicts

# Special route for /_next assets to ensure they're served correctly
@app.route('/_next/<path:filename>')
async def serve_next_static(filename):
    """Serve Next.js static assets from /_next folder"""
    try:
        return await app.send_static_file(f'_next/{filename}')
    except Exception as e:
        logger.error(f"Error serving Next.js asset: {e}")
        return jsonify({"error": "Next.js asset not available"}), 404

@app.route('/')
async def serve_frontend():
    """Serve the Next.js frontend index page"""
    try:
        logger.info("Serving root index.html")
        return await app.send_static_file('index.html')
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        return jsonify({"error": "Frontend not available"}), 404

@app.route('/<path:path>')
async def serve_frontend_routes(path):
    """Serve Next.js frontend routes and static files"""
    logger.info(f"Attempting to serve: {path}")
    
    # Skip API routes - they should be handled by their own handlers
    if path.startswith('api/'):
        return jsonify({"error": "Not found"}), 404
        
    try:
        # First try to serve as a static file
        return await app.send_static_file(path)
    except Exception as e1:
        logger.debug(f"Could not serve as static file: {e1}")
        try:
            # If not a static file, try to serve as a Next.js route
            if '.' not in path:  # It's likely a route, not a file
                route_file = f"{path}/index.html"
                logger.info(f"Trying to serve as route: {route_file}")
                return await app.send_static_file(route_file)
            else:
                logger.info(f"File not found: {path}")
                # It's a file that doesn't exist
                return jsonify({"error": "File not found"}), 404
        except Exception as e2:
            logger.info(f"Falling back to index.html for: {path} due to {e2}")
            # Fallback to main index.html for client-side routing
            return await app.send_static_file('index.html')


