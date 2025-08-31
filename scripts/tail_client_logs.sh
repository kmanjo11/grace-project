#!/usr/bin/env bash
set -euo pipefail
LOG_DIR="$(cd "$(dirname "$0")"/.. && pwd)/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/client.log"
# TimedRotatingFileHandler writes to client.log and rotates to client.log.YYYY-MM-DD
# Tail the active file and follow rotations if available on your system (requires tail -F on mac)
if command -v gtail >/dev/null 2>&1; then
  gtail -F "$LOG_FILE"
else
  tail -F "$LOG_FILE"
fi
