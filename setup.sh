#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

copy_example() {
  local example_file="$1"
  local target_file="$2"

  if [[ ! -f "$target_file" ]]; then
    cp "$example_file" "$target_file"
    echo "Created $target_file"
  else
    echo "Keeping existing $target_file"
  fi
}

copy_example ".env.example" ".env"
copy_example "front-end/.env.example" "front-end/.env"
copy_example "back-end/.env.example" "back-end/.env"

if command -v npm >/dev/null 2>&1; then
  echo "Installing frontend dependencies"
  (cd front-end && npm ci)
else
  echo "npm is not installed; skipping frontend dependency install"
fi

if command -v docker >/dev/null 2>&1; then
  echo "Validating Docker Compose configuration"
  docker compose config >/dev/null
else
  echo "Docker is not installed; skipping Compose validation"
fi

echo "Setup complete. Run ./scripts/dev.sh to start the full stack."
