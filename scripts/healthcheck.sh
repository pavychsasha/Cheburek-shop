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

BACKEND_URL="http://localhost:${BACKEND_PORT:-8091}/health"
FRONTEND_URL="http://localhost:${FRONTEND_PORT:-5178}"

echo "Checking backend: $BACKEND_URL"
curl -fsS "$BACKEND_URL"
echo

echo "Checking frontend: $FRONTEND_URL"
curl -fsS "$FRONTEND_URL" >/dev/null
echo "Frontend responded"
