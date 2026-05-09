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

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-cheburek_db}"

wait_for() {
  local service_name="$1"
  local command="$2"
  local attempts="${3:-60}"
  local delay_seconds="${4:-2}"

  echo "Waiting for ${service_name}"
  for _ in $(seq 1 "$attempts"); do
    if bash -c "$command" >/dev/null 2>&1; then
      echo "${service_name} is ready"
      return
    fi
    sleep "$delay_seconds"
  done

  echo "${service_name} did not become ready in time" >&2
  exit 1
}

wait_for \
  "PostgreSQL" \
  "docker compose exec -T postgres pg_isready -U '${POSTGRES_USER}' -d '${POSTGRES_DB}'"

wait_for \
  "MongoDB" \
  "docker compose exec -T mongo mongosh --quiet --eval 'db.runCommand({ ping: 1 }).ok'"

wait_for \
  "Redis" \
  "docker compose exec -T redis redis-cli ping"

wait_for \
  "MinIO" \
  "docker compose exec -T minio sh -c 'mc ready local >/dev/null 2>&1 || wget -q -O /dev/null http://127.0.0.1:9000/minio/health/live'"
