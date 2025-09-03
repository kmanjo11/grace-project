# Architecture Revision — 2025-09-03

This revision documents the Flash leverage integration changes that impact backend proxies, environment variables, and the UI positions aggregation.

## Summary of Changes

- Flash node-helper is now addressed via `FLASH_ADAPTER_BASE` (default `http://127.0.0.1:9020`).
- Backend Flash proxy routes in `src/api_server.py` point to the node-helper without `/flash` prefix and map order execution to `/order/execute`.
- Unified positions endpoint continues to aggregate GMGN spot + Flash leverage positions for the UI positions widget.

## Backend

- File: `src/api_server.py`
  - Added: `FLASH_ADAPTER_BASE = os.environ.get("FLASH_ADAPTER_BASE", "http://127.0.0.1:9020")`
  - Proxies updated:
    - `/api/flash/pools` -> `GET {FLASH_ADAPTER_BASE}/pools`
    - `/api/flash/markets` -> `GET {FLASH_ADAPTER_BASE}/markets`
    - `/api/flash/prices` -> `GET {FLASH_ADAPTER_BASE}/prices`
    - `/api/flash/positions` -> `GET {FLASH_ADAPTER_BASE}/positions?owner=<pubkey>`
    - `/api/flash/quote` -> `POST {FLASH_ADAPTER_BASE}/quote`
    - `/api/flash/order` -> `POST {FLASH_ADAPTER_BASE}/order/execute` (server-side signing)
    - `/api/flash/close` -> `POST {FLASH_ADAPTER_BASE}/close`
    - `/api/flash/tpsl` -> `POST {FLASH_ADAPTER_BASE}/tpsl`
    - `/api/flash/liquidation-price` -> `POST {FLASH_ADAPTER_BASE}/liquidation-price`
    - Liquidity: add/remove mapped to `{FLASH_ADAPTER_BASE}/liquidity/*`
  - Owner injection preserved:
    - Injects `owner` or `ownerPubkey` from `user_profile.internal_wallet.public_key` when missing.

## Flash Node-Helper

- File: `src/adapters/flash/node-helper/src/server.ts`
  - Listens on `process.env.FLASH_HELPER_PORT || 9020`.
  - Requires `ANCHOR_WALLET` (path to Solana keypair JSON) for server-side signing.
  - Exposes routes:
    - `GET /health`, `GET /pools`, `GET /markets`, `GET /prices`
    - `GET /positions?owner=<pubkey>`
    - `POST /quote`
    - `POST /order` (unsigned build for client signing)
    - `POST /order/execute` (server-signed and sent)
    - `POST /close` (unsigned close tx)
    - `POST /liquidation-price`
    - `POST /liquidity/add`, `POST /liquidity/remove`

## UI Positions Widget

- File: `src/ui/components/LightweightPositionsWidget.tsx`
  - Fetches unified positions from `/api/trading/positions`.
  - Backend aggregator normalizes and merges GMGN (spot) + Flash (leverage) positions.
  - For positions to appear, the executed trade's owner must match the wallet queried by the backend (injected from user profile).

## Environment Variables

- `FLASH_ADAPTER_BASE` (backend): defaults to `http://127.0.0.1:9020`.
- `FLASH_HELPER_PORT` (node-helper): default `9020`.
- `ANCHOR_WALLET` (node-helper): absolute path to service keypair JSON.
- `FLASH_RPC_URL` or `SOLANA_RPC_URL` (both sides): Solana RPC endpoint.
- `PYTHNET_RPC_URL` (node-helper prices): Pyth RPC endpoint for price queries.

## Local Dev Run (excerpt)

- Backend (port 9000) and UI (port 3000) unchanged per standardized ports.
- Flash node-helper Docker command (see `DEV_RUN_GUIDE.txt` Terminal D section):

```sh
docker run --rm -it \
  -p 9020:9020 \
  -e FLASH_HELPER_PORT=9020 \
  -e FLASH_NETWORK=mainnet-beta \
  -e SOLANA_RPC_URL="$SOLANA_RPC_URL" \
  -e FLASH_RPC_URL="$SOLANA_RPC_URL" \
  -e ANCHOR_WALLET=/app/keys/anchor.json \
  -e PYTHNET_RPC_URL="https://api.rpcpool.com/pythnet" \
  -v $(pwd)/deployment/keys/id.json:/app/keys/anchor.json:ro \
  -v $(pwd)/src/adapters/flash/node-helper:/app \
  -w /app \
  node:20-bookworm-slim sh -lc "npm -g i pnpm && pnpm i && node --loader ts-node/esm src/server.ts"
```

## Impact on E2E

- Server-signed GMGN and Flash trades will appear in the positions widget provided the `owner` used in execution equals the wallet used for positions lookup. Flash proxies inject owner automatically from the authenticated profile.
