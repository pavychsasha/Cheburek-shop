#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$BACKEND_DIR/.." && pwd)"

cd "$ROOT_DIR"

if [[ ! -f back-end/.env ]]; then
  cp back-end/.env.example back-end/.env
  echo "Created back-end/.env from back-end/.env.example"
fi

docker compose up -d postgres mongo redis
docker compose run --rm fastapi alembic upgrade head

echo "Backend setup complete."
