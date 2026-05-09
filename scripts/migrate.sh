#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose up -d postgres mongo redis
./scripts/wait-for-services.sh
docker compose build fastapi
docker compose run --rm fastapi alembic upgrade head
docker compose run --rm fastapi python -m app.actions.seed_products

echo "Database migrations and product seed complete."
