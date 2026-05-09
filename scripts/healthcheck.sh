#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

FRONTEND_PORT="${FRONTEND_PORT:-5178}"
BACKEND_PORT="${BACKEND_PORT:-8091}"
LOCAL_FRONTEND_DOMAIN="${LOCAL_FRONTEND_DOMAIN:-app.local.cheburek-shop.com}"
LOCAL_BACKEND_DOMAIN="${LOCAL_BACKEND_DOMAIN:-api.local.cheburek-shop.com}"

resolves_to_local() {
  local hostname="$1"

  python3 - "$hostname" <<'PY' >/dev/null 2>&1
import socket
import sys

try:
    address = socket.gethostbyname(sys.argv[1])
except OSError:
    sys.exit(1)

sys.exit(0 if address.startswith("127.") else 1)
PY
}

BACKEND_URL="http://localhost:${BACKEND_PORT}/health"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}"

if resolves_to_local "$LOCAL_BACKEND_DOMAIN" && resolves_to_local "$LOCAL_FRONTEND_DOMAIN"; then
  BACKEND_URL="http://${LOCAL_BACKEND_DOMAIN}:${BACKEND_PORT}/health"
  FRONTEND_URL="http://${LOCAL_FRONTEND_DOMAIN}:${FRONTEND_PORT}"
fi

export NO_PROXY="${NO_PROXY:-},${LOCAL_FRONTEND_DOMAIN},${LOCAL_BACKEND_DOMAIN}"
export no_proxy="${no_proxy:-},${LOCAL_FRONTEND_DOMAIN},${LOCAL_BACKEND_DOMAIN}"

echo "Checking backend: $BACKEND_URL"
curl -fsS "$BACKEND_URL"
echo

echo "Checking frontend: $FRONTEND_URL"
curl -fsS "$FRONTEND_URL" >/dev/null
echo "Frontend responded"
