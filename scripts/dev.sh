#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env || ! -f front-end/.env || ! -f back-end/.env ]] \
  || grep -q "generated-by-setup" .env front-end/.env back-end/.env 2>/dev/null; then
  ./setup.sh
fi

docker compose up --build
