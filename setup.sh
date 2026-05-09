#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

REGENERATE_SECRETS=false
SKIP_HOSTS=false
PROVISION=true

for arg in "$@"; do
  case "$arg" in
    --regenerate-secrets)
      REGENERATE_SECRETS=true
      ;;
    --skip-hosts)
      SKIP_HOSTS=true
      ;;
    --no-provision)
      PROVISION=false
      ;;
    --help|-h)
      echo "Usage: ./setup.sh [--regenerate-secrets] [--skip-hosts] [--no-provision]"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
  esac
done

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

read_env_value() {
  local file="$1"
  local key="$2"

  awk -F= -v key="$key" '$1 == key { sub(/^[^=]*=/, ""); print; exit }' "$file"
}

write_env_value() {
  local file="$1"
  local key="$2"
  local value="$3"
  local tmp_file="${file}.tmp.$$"

  if grep -q -E "^${key}=" "$file"; then
    awk -v key="$key" -v value="$value" '
      BEGIN { FS = OFS = "=" }
      $1 == key { print key "=" value; next }
      { print }
    ' "$file" > "$tmp_file"
  else
    cp "$file" "$tmp_file"
    printf "\n%s=%s\n" "$key" "$value" >> "$tmp_file"
  fi

  mv "$tmp_file" "$file"
}

random_secret() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
    return
  fi

  echo "openssl is required to generate local secrets" >&2
  exit 1
}

is_placeholder_secret() {
  local value="${1:-}"

  case "$value" in
    ""|"generated-by-setup"|"postgres"|local-*-change-me)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

ensure_secret() {
  local file="$1"
  local key="$2"
  local current_value

  current_value="$(read_env_value "$file" "$key")"
  if [[ "$REGENERATE_SECRETS" == "true" ]] || is_placeholder_secret "$current_value"; then
    write_env_value "$file" "$key" "$(random_secret)"
    echo "Generated $key in $file"
  fi
}

ensure_value() {
  local file="$1"
  local key="$2"
  local value="$3"
  local current_value

  current_value="$(read_env_value "$file" "$key")"
  if [[ -z "$current_value" ]]; then
    write_env_value "$file" "$key" "$value"
  fi
}

replace_value_if_matches() {
  local file="$1"
  local key="$2"
  local old_value="$3"
  local new_value="$4"
  local current_value

  current_value="$(read_env_value "$file" "$key")"
  if [[ -z "$current_value" || "$current_value" == "$old_value" ]]; then
    write_env_value "$file" "$key" "$new_value"
  fi
}

append_csv_value_if_missing() {
  local file="$1"
  local key="$2"
  local required_value="$3"
  local fallback_value="$4"
  local current_value

  current_value="$(read_env_value "$file" "$key")"
  if [[ -z "$current_value" ]]; then
    write_env_value "$file" "$key" "$fallback_value"
    return
  fi

  if [[ ",$current_value," != *",$required_value,"* ]]; then
    write_env_value "$file" "$key" "${required_value},${current_value}"
  fi
}

configure_hosts() {
  local frontend_domain="$1"
  local backend_domain="$2"
  local admin_domain="$3"
  local hosts_entry="127.0.0.1 ${frontend_domain} ${backend_domain} ${admin_domain}"

  if grep -Eq "^[[:space:]]*127\\.0\\.0\\.1[[:space:]].*\\b${frontend_domain}\\b" /etc/hosts \
    && grep -Eq "^[[:space:]]*127\\.0\\.0\\.1[[:space:]].*\\b${backend_domain}\\b" /etc/hosts \
    && grep -Eq "^[[:space:]]*127\\.0\\.0\\.1[[:space:]].*\\b${admin_domain}\\b" /etc/hosts; then
    echo "Local hostnames are already configured."
    return
  fi

  echo "Local hostname entry needed:"
  echo "$hosts_entry"

  if [[ ! -t 0 ]]; then
    echo "Non-interactive shell detected; add the entry manually or rerun setup in a terminal."
    return
  fi

  read -r -p "Add this entry to /etc/hosts with sudo? [y/N] " response
  case "$response" in
    y|Y|yes|YES)
      printf "%s\n" "$hosts_entry" | sudo tee -a /etc/hosts >/dev/null
      echo "Updated /etc/hosts."
      ;;
    *)
      echo "Skipped /etc/hosts update."
      ;;
  esac
}

copy_example ".env.example" ".env"
copy_example "front-end/.env.example" "front-end/.env"
copy_example "back-end/.env.example" "back-end/.env"

ensure_value ".env" "FRONTEND_PORT" "5178"
ensure_value ".env" "BACKEND_PORT" "8091"
ensure_value ".env" "LOCAL_HTTP_PORT" "80"
ensure_value ".env" "POSTGRES_PORT" "55432"
ensure_value ".env" "MONGO_PORT" "27018"
ensure_value ".env" "REDIS_PORT" "6380"
ensure_value ".env" "MINIO_API_PORT" "9000"
ensure_value ".env" "MINIO_CONSOLE_PORT" "9001"
ensure_value ".env" "MINIO_BUCKET" "cheburek-product-images"
ensure_value ".env" "MAX_IMAGE_UPLOAD_MB" "5"
ensure_value ".env" "DEFAULT_CURRENCY" "UAH"
ensure_value ".env" "SUPPORTED_CURRENCIES" "UAH,USD,EUR"
ensure_value ".env" "CURRENCY_RATES" "UAH:1,USD:0.024,EUR:0.022"
ensure_value ".env" "CURRENCY_SYMBOLS" "UAH:₴,USD:$,EUR:€"
ensure_value ".env" "LOCAL_FRONTEND_DOMAIN" "app.local.cheburek-shop.com"
ensure_value ".env" "LOCAL_BACKEND_DOMAIN" "api.local.cheburek-shop.com"
ensure_value ".env" "LOCAL_ADMIN_DOMAIN" "admin.local.cheburek-shop.com"
ensure_value ".env" "POSTGRES_USER" "postgres"
ensure_value ".env" "POSTGRES_DB" "cheburek_db"
ensure_value ".env" "POSTGRES_TEST_DB" "test_db"
ensure_value ".env" "MONGO_DATABASE_NAME" "cheburek_mongo_db"
ensure_value ".env" "MONGO_TEST_DATABASE_NAME" "test_cheburek_mongo_db"
ensure_value ".env" "REDIS_DB" "0"

ensure_secret ".env" "POSTGRES_PASSWORD"
ensure_secret ".env" "RESET_PASSWORD_TOKEN_SECRET"
ensure_secret ".env" "VERIFICATION_TOKEN_SECRET"
ensure_secret ".env" "SESSION_SECRET_KEY"
ensure_secret ".env" "ADMIN_PASSWORD"
ensure_secret ".env" "MINIO_ROOT_USER"
ensure_secret ".env" "MINIO_ROOT_PASSWORD"

FRONTEND_PORT="$(read_env_value ".env" "FRONTEND_PORT")"
BACKEND_PORT="$(read_env_value ".env" "BACKEND_PORT")"
LOCAL_HTTP_PORT="$(read_env_value ".env" "LOCAL_HTTP_PORT")"
POSTGRES_PORT="$(read_env_value ".env" "POSTGRES_PORT")"
MONGO_PORT="$(read_env_value ".env" "MONGO_PORT")"
REDIS_PORT="$(read_env_value ".env" "REDIS_PORT")"
MINIO_API_PORT="$(read_env_value ".env" "MINIO_API_PORT")"
MINIO_CONSOLE_PORT="$(read_env_value ".env" "MINIO_CONSOLE_PORT")"
MINIO_BUCKET="$(read_env_value ".env" "MINIO_BUCKET")"
MAX_IMAGE_UPLOAD_MB="$(read_env_value ".env" "MAX_IMAGE_UPLOAD_MB")"
DEFAULT_CURRENCY="$(read_env_value ".env" "DEFAULT_CURRENCY")"
SUPPORTED_CURRENCIES="$(read_env_value ".env" "SUPPORTED_CURRENCIES")"
CURRENCY_RATES="$(read_env_value ".env" "CURRENCY_RATES")"
CURRENCY_SYMBOLS="$(read_env_value ".env" "CURRENCY_SYMBOLS")"
LOCAL_FRONTEND_DOMAIN="$(read_env_value ".env" "LOCAL_FRONTEND_DOMAIN")"
LOCAL_BACKEND_DOMAIN="$(read_env_value ".env" "LOCAL_BACKEND_DOMAIN")"
LOCAL_ADMIN_DOMAIN="$(read_env_value ".env" "LOCAL_ADMIN_DOMAIN")"
POSTGRES_USER="$(read_env_value ".env" "POSTGRES_USER")"
POSTGRES_PASSWORD="$(read_env_value ".env" "POSTGRES_PASSWORD")"
POSTGRES_DB="$(read_env_value ".env" "POSTGRES_DB")"
POSTGRES_TEST_DB="$(read_env_value ".env" "POSTGRES_TEST_DB")"
RESET_PASSWORD_TOKEN_SECRET="$(read_env_value ".env" "RESET_PASSWORD_TOKEN_SECRET")"
VERIFICATION_TOKEN_SECRET="$(read_env_value ".env" "VERIFICATION_TOKEN_SECRET")"
SESSION_SECRET_KEY="$(read_env_value ".env" "SESSION_SECRET_KEY")"
MINIO_ROOT_USER="$(read_env_value ".env" "MINIO_ROOT_USER")"
MINIO_ROOT_PASSWORD="$(read_env_value ".env" "MINIO_ROOT_PASSWORD")"
ADMIN_EMAIL="$(read_env_value ".env" "ADMIN_EMAIL")"
if [[ -z "$ADMIN_EMAIL" || "$ADMIN_EMAIL" == "generated-by-setup" ]]; then
  write_env_value ".env" "ADMIN_EMAIL" "admin@${LOCAL_ADMIN_DOMAIN}"
  ADMIN_EMAIL="$(read_env_value ".env" "ADMIN_EMAIL")"
fi
ADMIN_PASSWORD="$(read_env_value ".env" "ADMIN_PASSWORD")"

LOCAL_HTTP_PORT_SUFFIX=""
if [[ "$LOCAL_HTTP_PORT" != "80" ]]; then
  LOCAL_HTTP_PORT_SUFFIX=":${LOCAL_HTTP_PORT}"
fi

LOCAL_API_BASE_URL="http://${LOCAL_BACKEND_DOMAIN}${LOCAL_HTTP_PORT_SUFFIX}/api/v1"
LOCAL_MEDIA_PUBLIC_BASE_URL="http://${LOCAL_BACKEND_DOMAIN}${LOCAL_HTTP_PORT_SUFFIX}/media"
LOCAL_FRONTEND_ORIGIN="http://${LOCAL_FRONTEND_DOMAIN}${LOCAL_HTTP_PORT_SUFFIX}"
LOCAL_ADMIN_ORIGIN="http://${LOCAL_ADMIN_DOMAIN}${LOCAL_HTTP_PORT_SUFFIX}"
LOCAL_DIRECT_FRONTEND_ORIGIN="http://${LOCAL_FRONTEND_DOMAIN}:${FRONTEND_PORT}"
LOCAL_DIRECT_ADMIN_ORIGIN="http://${LOCAL_ADMIN_DOMAIN}:${FRONTEND_PORT}"
LOCAL_CORS_ORIGINS="${LOCAL_FRONTEND_ORIGIN},${LOCAL_ADMIN_ORIGIN},${LOCAL_DIRECT_FRONTEND_ORIGIN},${LOCAL_DIRECT_ADMIN_ORIGIN},http://localhost:${FRONTEND_PORT},http://127.0.0.1:${FRONTEND_PORT},http://react:${FRONTEND_PORT}"
LOCAL_ALLOWED_HOSTS="${LOCAL_FRONTEND_DOMAIN},${LOCAL_ADMIN_DOMAIN},localhost,127.0.0.1"

replace_value_if_matches ".env" "VITE_API_BASE_URL" "http://localhost:8091/api/v1" "$LOCAL_API_BASE_URL"
replace_value_if_matches ".env" "VITE_API_BASE_URL" "http://${LOCAL_BACKEND_DOMAIN}:${BACKEND_PORT}/api/v1" "$LOCAL_API_BASE_URL"
write_env_value ".env" "MINIO_ENDPOINT" "localhost:${MINIO_API_PORT}"
write_env_value ".env" "MINIO_PUBLIC_BASE_URL" "$LOCAL_MEDIA_PUBLIC_BASE_URL"
append_csv_value_if_missing ".env" "CORS_ALLOWED_ORIGINS" "$LOCAL_FRONTEND_ORIGIN" "$LOCAL_CORS_ORIGINS"
append_csv_value_if_missing ".env" "CORS_ALLOWED_ORIGINS" "$LOCAL_ADMIN_ORIGIN" "$LOCAL_CORS_ORIGINS"
write_env_value ".env" "VITE_DEV_ALLOWED_HOSTS" "$LOCAL_ALLOWED_HOSTS"

write_env_value "front-end/.env" "VITE_API_BASE_URL" "$LOCAL_API_BASE_URL"
write_env_value "front-end/.env" "VITE_DEV_SERVER_HOST" "0.0.0.0"
write_env_value "front-end/.env" "VITE_DEV_SERVER_PORT" "$FRONTEND_PORT"
write_env_value "front-end/.env" "VITE_DEV_ALLOWED_HOSTS" "$LOCAL_ALLOWED_HOSTS"

write_env_value "back-end/.env" "APP_CONFIG__RUN__HOST" "127.0.0.1"
write_env_value "back-end/.env" "APP_CONFIG__RUN__PORT" "$BACKEND_PORT"
write_env_value "back-end/.env" "APP_CONFIG__DB__URL" "postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}"
write_env_value "back-end/.env" "APP_CONFIG__DB__TEST_URL" "postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_TEST_DB}"
write_env_value "back-end/.env" "APP_CONFIG__ACCESS_TOKEN__RESET_PASSWORD_TOKEN_SECRET" "$RESET_PASSWORD_TOKEN_SECRET"
write_env_value "back-end/.env" "APP_CONFIG__ACCESS_TOKEN__VERIFICATION_TOKEN_SECRET" "$VERIFICATION_TOKEN_SECRET"
write_env_value "back-end/.env" "APP_CONFIG__MONGO_DB__HOST" "localhost"
write_env_value "back-end/.env" "APP_CONFIG__MONGO_DB__PORT" "$MONGO_PORT"
write_env_value "back-end/.env" "APP_CONFIG__REDIS__HOST" "localhost"
write_env_value "back-end/.env" "APP_CONFIG__REDIS__PORT" "$REDIS_PORT"
write_env_value "back-end/.env" "APP_CONFIG__MEDIA__ENDPOINT" "localhost:${MINIO_API_PORT}"
write_env_value "back-end/.env" "APP_CONFIG__MEDIA__ACCESS_KEY" "$MINIO_ROOT_USER"
write_env_value "back-end/.env" "APP_CONFIG__MEDIA__SECRET_KEY" "$MINIO_ROOT_PASSWORD"
write_env_value "back-end/.env" "APP_CONFIG__MEDIA__BUCKET" "$MINIO_BUCKET"
write_env_value "back-end/.env" "APP_CONFIG__MEDIA__PUBLIC_BASE_URL" "$LOCAL_MEDIA_PUBLIC_BASE_URL"
write_env_value "back-end/.env" "APP_CONFIG__MEDIA__SECURE" "false"
write_env_value "back-end/.env" "APP_CONFIG__MEDIA__MAX_IMAGE_UPLOAD_MB" "$MAX_IMAGE_UPLOAD_MB"
write_env_value "back-end/.env" "APP_CONFIG__CURRENCY__BASE_CURRENCY" "UAH"
write_env_value "back-end/.env" "APP_CONFIG__CURRENCY__DEFAULT_CURRENCY" "$DEFAULT_CURRENCY"
write_env_value "back-end/.env" "APP_CONFIG__CURRENCY__SUPPORTED_CURRENCIES" "$SUPPORTED_CURRENCIES"
write_env_value "back-end/.env" "APP_CONFIG__CURRENCY__CURRENCY_RATES" "$CURRENCY_RATES"
write_env_value "back-end/.env" "APP_CONFIG__CURRENCY__CURRENCY_SYMBOLS" "$CURRENCY_SYMBOLS"
write_env_value "back-end/.env" "APP_CONFIG__SESSION__SECRET_KEY" "$SESSION_SECRET_KEY"
write_env_value "back-end/.env" "APP_CONFIG__CORS__ALLOWED_ORIGINS" "$LOCAL_CORS_ORIGINS"
write_env_value "back-end/.env" "ADMIN_EMAIL" "$ADMIN_EMAIL"
write_env_value "back-end/.env" "ADMIN_PASSWORD" "$ADMIN_PASSWORD"

if [[ "$SKIP_HOSTS" != "true" ]]; then
  configure_hosts "$LOCAL_FRONTEND_DOMAIN" "$LOCAL_BACKEND_DOMAIN" "$LOCAL_ADMIN_DOMAIN"
fi

if command -v npm >/dev/null 2>&1; then
  echo "Installing frontend dependencies"
  (cd front-end && npm ci)
else
  echo "npm is not installed; skipping frontend dependency install"
fi

if command -v docker >/dev/null 2>&1; then
  echo "Validating Docker Compose configuration"
  docker compose config >/dev/null
  if [[ "$PROVISION" == "true" ]]; then
    echo "Provisioning local databases"
    ./scripts/migrate.sh
    echo "Bootstrapping local admin user"
    docker compose run --rm fastapi python -m app.actions.create_super_user
  fi
else
  if [[ "$PROVISION" == "true" ]]; then
    echo "Docker is required to provision local services. Install Docker or rerun with --no-provision." >&2
    exit 1
  fi
  echo "Docker is not installed; skipping Compose validation"
fi

echo "Setup complete. Run ./start.sh to start the full stack."
