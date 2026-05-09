#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$BACKEND_DIR/.." && pwd)"

cd "$ROOT_DIR"

if [[ ! -f .env || ! -f back-end/.env ]] || grep -q "generated-by-setup" .env back-end/.env; then
  ./setup.sh
fi

docker compose up -d postgres mongo redis
docker compose run --rm fastapi alembic upgrade head

echo "Backend setup complete."
