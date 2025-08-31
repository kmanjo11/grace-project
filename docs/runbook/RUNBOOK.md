# Grace Project Runbook (Canonical)

This is the single source of truth for running Grace locally and via Docker. Older setup docs are deprecated; see the Deprecation section below.

## System Overview

- Backend (Python/Quart) runs on port 9000.
- Frontend (Next.js) runs on port 3000.
- Development workflow: run backend and frontend in separate terminals (no Docker).
- Docker: used for integrated runs; backend Dockerfile lives in `deployment/Dockerfile`, UI Dockerfile lives in the repo root (builds `src/` and `src/ui/`).
- Data/logs: server writes logs under `data/logs/`.

## Prerequisites

- Python 3.10+
- Node 18+ and pnpm
- Redis running locally (separate terminal), required by chat session services
- OpenAI API access

## Environment

Store all env vars in the repo root `.env` and export them for both processes:

```bash
# from repo root
set -a
source /Users/wonkasworld/Downloads/grace-project/.env
set +a
```

Minimum required (examples):

- OPENAI_API_KEY=sk-...
- OPENAI_PROJECT=proj_...
- BACKEND_PORT=9000 (if used)
- NEXT_PUBLIC_API_BASE=http://localhost:9000
- Optional dev toggles:
  - NEXT_PUBLIC_DISABLE_STATE_PERSIST=0|1
  - NEXT_PUBLIC_ENABLE_CLIENT_LOGS=0|1

Ports are standardized: backend 9000, frontend 3000.

## Running in Development (recommended)

Use two terminals.

1) Backend (from repo root):

```bash
python3 -m src.run_server
```

2) Frontend (from `src/ui/`):

```bash
pnpm install
# Optional UI toggles during run
#   NEXT_PUBLIC_DISABLE_STATE_PERSIST=1 NEXT_PUBLIC_ENABLE_CLIENT_LOGS=1 \
#   pnpm next start
pnpm next start
# or pnpm dev if you prefer dev server
```

Notes:
- Ensure you exported `.env` beforehand.
- Client logs will stream to `/api/logs` and server writes to `data/logs/`.
- Scroll and state persistence can be toggled via `NEXT_PUBLIC_DISABLE_STATE_PERSIST`.

## Redis

Run Redis locally in a separate terminal before starting backend (Grace uses Redis for session/state services):

```bash
# Option A: Homebrew service
brew services start redis
# Option B: direct
redis-server
```

Default URL: `redis://localhost:6379` (set REDIS_URL in `.env` if different).

## OpenAI / Open Interpreter connectivity

- Backend reads `OPENAI_API_KEY` (and optionally `OPENAI_PROJECT`) from the environment during initialization.
- Ensure these are exported before launching the backend.

Quick sanity checks:

- Confirm env visible in Python:
```bash
python3 - <<'PY'
import os
print('Has OPENAI_API_KEY?', bool(os.environ.get('OPENAI_API_KEY')))
print('OPENAI_PROJECT set?', bool(os.environ.get('OPENAI_PROJECT')))
PY
```

- Backend health and history:
```bash
curl -s http://localhost:9000/api/logs | jq .
# If authenticated endpoints are enabled in your environment:
# curl -H "Authorization: Bearer <your-dev-token>" http://localhost:9000/api/chat/history/<session_id>
```

If these succeed, the backend has access to the API key and is responsive. The Open Interpreter core is initialized inside backend startup using your `OPENAI_API_KEY`.

### Python quick test (OpenAI client)

Run this in a terminal to confirm the Python client can reach OpenAI with your env:

```python
import os
from openai import OpenAI

print('Has key?', bool(os.environ.get('OPENAI_API_KEY')))
client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello from Grace."}]
)
print(resp.choices[0].message.content)
```

If this prints a greeting, your API key and network are configured.

### How the backend initializes Open Interpreter

The backend creates the Interpreter core during startup using `OPENAI_API_KEY` (and project if present). If either is missing, startup will raise an error. Ensure you export `.env` before `python3 -m src.run_server`.

## Logging

- Client logs: batched to `POST /api/logs` (dev no-op GET is provided). Controlled by `NEXT_PUBLIC_ENABLE_CLIENT_LOGS`.
- Server logs: `data/logs/`.

## Docker (optional)

Only use Docker when you need integrated containers. For development, prefer native processes as above.

- Backend container uses `deployment/Dockerfile` and `deployment/docker-compose.yml`.
- Frontend container (UI) uses the root `Dockerfile` (builds from `/src` and `/src/ui`).

When using Docker:
- Ensure `.env` exists at repo root and contains all required secrets/vars.
- Verify ports map to 9000 (backend) and 3000 (frontend) in compose.
- If Redis is not part of the compose, run it locally or add a Redis service to your compose file and point `REDIS_URL` to it.

## Common Commands

- Backend: `python3 -m src.run_server` (run from repo root)
- Frontend: `pnpm next start` (run from `src/ui/`)
- Export env: `set -a; source ./.env; set +a`
- Redis: `brew services start redis` (or `redis-server`)

## Deprecation of older docs

The following files are superseded by this RUNBOOK. They should link here and be treated as historical or detailed references:

- `GETTING_STARTED.md`
- `documentation.md`
- `deployment/DOCKER_GUIDE.md` and `src/Readme/DOCKER_GUIDE.md`
- `src/Docker Fixed/Grace Project - Docker Setup Guide.md`

If you encounter discrepancies, this RUNBOOK takes precedence.
