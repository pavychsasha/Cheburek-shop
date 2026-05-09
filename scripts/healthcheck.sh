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
LOCAL_HTTP_PORT="${LOCAL_HTTP_PORT:-80}"
LOCAL_FRONTEND_DOMAIN="${LOCAL_FRONTEND_DOMAIN:-app.local.cheburek-shop.com}"
LOCAL_BACKEND_DOMAIN="${LOCAL_BACKEND_DOMAIN:-api.local.cheburek-shop.com}"
LOCAL_ADMIN_DOMAIN="${LOCAL_ADMIN_DOMAIN:-admin.local.cheburek-shop.com}"

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
ADMIN_URL=""
LOCAL_HTTP_PORT_SUFFIX=""
if [[ "$LOCAL_HTTP_PORT" != "80" ]]; then
  LOCAL_HTTP_PORT_SUFFIX=":${LOCAL_HTTP_PORT}"
fi

if resolves_to_local "$LOCAL_BACKEND_DOMAIN" \
  && resolves_to_local "$LOCAL_FRONTEND_DOMAIN" \
  && resolves_to_local "$LOCAL_ADMIN_DOMAIN"; then
  BACKEND_URL="http://${LOCAL_BACKEND_DOMAIN}${LOCAL_HTTP_PORT_SUFFIX}/health"
  FRONTEND_URL="http://${LOCAL_FRONTEND_DOMAIN}${LOCAL_HTTP_PORT_SUFFIX}"
  ADMIN_URL="http://${LOCAL_ADMIN_DOMAIN}${LOCAL_HTTP_PORT_SUFFIX}"
fi

export NO_PROXY="${NO_PROXY:-},${LOCAL_FRONTEND_DOMAIN},${LOCAL_BACKEND_DOMAIN},${LOCAL_ADMIN_DOMAIN}"
export no_proxy="${no_proxy:-},${LOCAL_FRONTEND_DOMAIN},${LOCAL_BACKEND_DOMAIN},${LOCAL_ADMIN_DOMAIN}"

echo "Checking backend: $BACKEND_URL"
curl -fsS "$BACKEND_URL"
echo

echo "Checking frontend: $FRONTEND_URL"
curl -fsS "$FRONTEND_URL" >/dev/null
echo "Frontend responded"

if [[ -n "$ADMIN_URL" ]]; then
  echo "Checking admin portal: $ADMIN_URL"
  curl -fsS "$ADMIN_URL" >/dev/null
  echo "Admin portal responded"
else
  echo "Admin hostname is not configured in /etc/hosts; skipping admin portal hostname check."
fi
