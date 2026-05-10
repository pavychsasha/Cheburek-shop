#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose up -d postgres mongo redis minio translator
./scripts/wait-for-services.sh
docker compose build fastapi
docker compose run --rm fastapi alembic upgrade head
docker compose run --rm fastapi python -m app.actions.seed_products
docker compose run --rm fastapi python -m app.actions.backfill_product_translations
docker compose run --rm fastapi python -m app.actions.seed_demo_orders
docker compose run --rm fastapi python -m app.actions.seed_demo_analytics

echo "Database migrations, product seed, translation backfill, demo orders, and analytics seed complete."
