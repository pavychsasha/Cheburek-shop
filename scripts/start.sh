#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DETACHED=false

for arg in "$@"; do
  case "$arg" in
    --detach|--detached|-d)
      DETACHED=true
      ;;
    --help|-h)
      echo "Usage: ./start.sh [--detached]"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
  esac
done

if [[ ! -f .env || ! -f front-end/.env || ! -f back-end/.env ]] \
  || grep -q "generated-by-setup" .env front-end/.env back-end/.env 2>/dev/null; then
  ./setup.sh
else
  ./scripts/migrate.sh
  docker compose run --rm fastapi python -m app.actions.create_super_user
fi

if [[ "$DETACHED" == "true" ]]; then
  docker compose up --build --wait --wait-timeout 180
else
  docker compose up --build
fi
