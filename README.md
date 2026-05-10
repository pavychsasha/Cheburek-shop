# Cheburek Shop

Cheburek Shop is a React storefront backed by a FastAPI API, PostgreSQL, MongoDB, and Redis.
The same frontend service also hosts a protected admin CMS for catalog, media, orders, users, analytics, and currency settings.

## Stack

- Frontend: React 18, Vite, TypeScript, Redux Toolkit, SCSS modules, npm
- Backend: Python 3.12, FastAPI, Poetry, SQLAlchemy async, Alembic, Beanie, Redis, MinIO, pytest
- Services: PostgreSQL 16, MongoDB 7, Redis 7, MinIO object storage
- Local orchestration: Docker Compose

## Project Contributors

- Frontend lead: [@ost1qq](https://github.com/ost1qq)

## Local URLs

Preferred local-domain URLs:

| Service | Default URL |
| --- | --- |
| Frontend | `http://app.local.cheburek-shop.com` |
| Admin portal | `http://admin.local.cheburek-shop.com` |
| Backend API | `http://api.local.cheburek-shop.com/api/v1` |
| Backend health | `http://api.local.cheburek-shop.com/health` |
| Public media | `http://api.local.cheburek-shop.com/media/...` |

Localhost fallback URLs:

| Service | Default URL |
| --- | --- |
| Frontend | `http://localhost:5178` |
| Backend API | `http://localhost:8091/api/v1` |
| Backend health | `http://localhost:8091/health` |
| Local HTTP proxy | `80` |
| PostgreSQL host port | `55432` |
| MongoDB host port | `27018` |
| Redis host port | `6380` |
| MinIO API port | `9000` |
| MinIO console | `http://localhost:9001` |

The friendly local-domain URLs are served through the local proxy on `LOCAL_HTTP_PORT=80`, so they do not need explicit ports. Direct service ports are intentionally offset from common defaults. Override them in `.env` if needed.

## Quick Start

```bash
./setup.sh
./start.sh
```

`setup.sh` creates local env files, generates local-only secrets, installs frontend dependencies when npm is available, validates Docker Compose, starts PostgreSQL, MongoDB, Redis, and MinIO, waits for them to become healthy, runs migrations, seeds the product catalog, category visuals, product media, product tags, and local demo orders idempotently, backfills configured product-language drafts, bootstraps the local admin user, and offers to add these hostnames to `/etc/hosts`:

```text
127.0.0.1 app.local.cheburek-shop.com api.local.cheburek-shop.com admin.local.cheburek-shop.com
```

If you do not want the script to touch `/etc/hosts`, run:

```bash
./setup.sh --skip-hosts
```

Then add the hosts entry manually or use the storefront localhost fallback URL.

If you only want env generation and dependency installation without starting Docker services, run:

```bash
./setup.sh --no-provision
```

`start.sh` is the simple app runner. It provisions missing setup automatically, keeps migrations/seeding/admin bootstrap idempotent, and starts the API plus frontend with Docker Compose health checks. `scripts/dev.sh` is kept as a compatibility alias for `start.sh`.

To run the full stack in the background:

```bash
./start.sh --detached
```

Run migrations and the idempotent product seed after services are available:

```bash
./scripts/migrate.sh
```

The product seed creates missing seed products, uploads deterministic local product and category images to MinIO, updates known seed product fields and tags by English product name, and backfills missing configured product-language drafts. It does not delete unrelated products, carts, or orders. A destructive seed reset is available only as an explicit local maintenance action:

```bash
docker compose run --rm fastapi python -m app.actions.seed_products --reset
```

Check the running stack:

```bash
./scripts/healthcheck.sh
```

## Environment And Secret Safety

Committed `.env.example` files contain placeholders only. Real local values are generated into ignored `.env` files:

```bash
.env
front-end/.env
back-end/.env
```

Do not commit generated `.env` files, local certificates, private keys, or Compose override files. The setup script does not print generated secrets.

Important root `.env` values:

- `LOCAL_FRONTEND_DOMAIN`: local frontend hostname
- `LOCAL_BACKEND_DOMAIN`: local API hostname
- `LOCAL_ADMIN_DOMAIN`: local admin hostname
- `LOCAL_HTTP_PORT`: local proxy HTTP port; use `80` for no-port URLs
- `FRONTEND_PORT`: frontend dev server port
- `BACKEND_PORT`: backend API port
- `POSTGRES_PORT`: host PostgreSQL port
- `MONGO_PORT`: host MongoDB port
- `REDIS_PORT`: host Redis port
- `MINIO_API_PORT`: host MinIO API port
- `MINIO_CONSOLE_PORT`: host MinIO console port
- `TRANSLATOR_PORT`: host port for the local LibreTranslate service
- `MINIO_ROOT_USER`: generated local MinIO access key
- `MINIO_ROOT_PASSWORD`: generated local MinIO secret key
- `MINIO_BUCKET`: local product image bucket
- `MINIO_PUBLIC_BASE_URL`: public media URL served through the backend
- `MAX_IMAGE_UPLOAD_MB`: admin image upload limit
- `DEFAULT_CURRENCY`: default display currency
- `SUPPORTED_CURRENCIES`: comma-separated display currencies
- `CURRENCY_RATES`: static display rates from base UAH
- `CURRENCY_SYMBOLS`: display symbols for supported currencies
- `FALLBACK_PROFIT_MARGIN`: estimated margin for legacy order rows without saved cost
- `PRODUCT_LANGUAGES`: comma-separated product translation languages
- `AUTO_TRANSLATE_PRODUCTS`: enables local auto-translation for missing product languages
- `TRANSLATION_ENABLED`: enables the local translation service integration
- `TRANSLATION_TIMEOUT_SECONDS`: backend timeout for translation requests
- `TRANSLATION_SOURCE_LANGUAGE`: source language used for generated product translations
- `VITE_API_BASE_URL`: browser API base URL
- `CORS_ALLOWED_ORIGINS`: comma-separated frontend origins allowed by the API
- `POSTGRES_PASSWORD`: generated local database password
- `RESET_PASSWORD_TOKEN_SECRET`: generated local reset-token secret
- `VERIFICATION_TOKEN_SECRET`: generated local verification-token secret
- `SESSION_SECRET_KEY`: generated local session secret
- `ACCESS_TOKEN_LIFETIME_SECONDS`: bearer token lifetime; default local value is `2592000` seconds, or 30 days
- `ADMIN_EMAIL`: generated local admin email
- `ADMIN_PASSWORD`: generated local admin password

Regenerate local secrets only when you intentionally want to rotate local development values:

```bash
./setup.sh --regenerate-secrets
```

If PostgreSQL was already initialized with the old generated password, reset local service volumes before starting again:

```bash
docker compose down -v
```

That removes local database data.

Local admin credentials are generated into ignored `.env` files. Read them locally when signing in to the admin portal, and do not copy them into commits, issue text, screenshots, chat messages, or documentation.

## Development Commands

Frontend:

```bash
cd front-end
npm ci
npm run dev
npm run lint
npm run typecheck
npm run build
npm audit
```

Backend with Poetry:

```bash
cd back-end
poetry install
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8091 --reload
poetry run alembic upgrade head
poetry run pytest
poetry run pip-audit
```

Backend through Docker Compose:

```bash
docker compose build fastapi
docker compose up -d postgres mongo redis minio translator fastapi
curl http://localhost:8091/health
```

Admin and seed helpers:

```bash
docker compose run --rm fastapi python -m app.actions.seed_products
docker compose run --rm fastapi python -m app.actions.seed_demo_orders
docker compose run --rm fastapi python -m app.actions.seed_demo_analytics
docker compose run --rm fastapi python -m app.actions.backfill_product_translations
docker compose run --rm fastapi python -m app.actions.create_super_user
```

## Product Languages And SEO

- Product creation in the admin CMS uses translation tabs instead of separate hardcoded fields.
- Product tags are managed in the admin CMS and power similar-item recommendations in the storefront.
- Add global product languages in Admin Settings, then run the product translation backfill action from the same screen.
- Missing translations are generated through the local LibreTranslate service when enabled, then remain editable in the admin CMS before publishing.
- Product images are uploaded by drag-and-drop in the admin CMS. The raw media URL is kept internally but is not edited directly in the product form.
- The storefront includes baseline SEO metadata, Open Graph/Twitter metadata, canonical URLs, and restaurant structured data.
- The admin host sets `noindex,nofollow` at runtime.
- For production-grade per-product SEO, add stable product detail routes plus server-side rendering or prerendering so crawlers receive product-specific HTML.

## CMS, Analytics, And Demo Data

- The admin CMS includes catalog/media management, product costs, product tags, product languages, searchable orders/users, order status and private fulfillment notes, currency/profit settings, and dashboard analytics.
- Profit analytics show revenue, recorded cost, gross profit, estimated profit for legacy rows, margin, and average order value.
- Customer order notes are collected at checkout and private admin notes are editable from order detail.
- Dashboard widget visibility, order, chart type, timespan, and periodization are stored per admin user in the backend.
- Visitor analytics are first-party and privacy-safe: the app stores an anonymous visitor cookie, records aggregate daily unique visitors and page views, and does not persist raw IP addresses.
- Similar-item recommendations use shared product tags first and category fallback second.
- Local demo orders and visitor/page-view analytics are seeded by default so dashboard charts are useful on a fresh setup. Demo seeds are idempotent and local-development oriented.

## Troubleshooting

- Compose reports a missing secret: run `./setup.sh` before starting services.
- Local-domain URLs do not resolve: add the hosts entry shown by `./setup.sh`, then retry.
- Admin portal does not open: confirm `admin.local.cheburek-shop.com` is in `/etc/hosts` and `VITE_DEV_ALLOWED_HOSTS`.
- Product images do not load: confirm `/health` reports `minio: ok`, then rerun `./scripts/migrate.sh` to recreate seed media.
- MinIO console login is needed: read the generated local MinIO values from ignored `.env`; do not copy them into documentation or commits.
- Currency selector shows stale values: reload settings in the admin Settings panel or refresh the page after saving currency changes.
- Product translation languages look stale: reload Admin Settings, save the language list, then run the backfill action.
- Auto-translation is unavailable: confirm the `translator` container is healthy and `TRANSLATION_ENABLED=true`, then rerun the backfill or use the Products panel translation action. First startup can take longer while LibreTranslate downloads local models into the Docker volume.
- Port already in use: update `.env`, `front-end/.env`, and `back-end/.env` so ports, `VITE_API_BASE_URL`, and `CORS_ALLOWED_ORIGINS` stay aligned. If host port `80` is busy, set `LOCAL_HTTP_PORT` to another value and include that port in local-domain URLs.
- Frontend cannot reach the API: confirm `VITE_API_BASE_URL` points to the backend URL visible from the browser.
- Storefront works on localhost but local domains fail: rerun `./setup.sh` in a terminal and accept or manually add the printed hosts entry.
- CORS errors: add the frontend origin to `CORS_ALLOWED_ORIGINS`.
- Health check returns `degraded`: PostgreSQL, MongoDB, Redis, MinIO, or the translator is not reachable from the backend container.
- Compose waits indefinitely or reports an unhealthy service: inspect logs with `docker compose logs <service>` and rerun `./setup.sh`.
- Backend tests require PostgreSQL, MongoDB, and Redis. Start dependencies before running the full pytest suite.
- After rotating local secrets, reset local volumes if database authentication no longer works.
- Admin login fails after rotating secrets: rerun `docker compose run --rm fastapi python -m app.actions.create_super_user` so the local admin password matches the generated env value.
- Users are signed out too quickly: confirm `ACCESS_TOKEN_LIFETIME_SECONDS` in root `.env` and `APP_CONFIG__ACCESS_TOKEN__LIFETIME_SECONDS` in `back-end/.env` are set to the desired duration, then restart the API container.

## Dependency And Security Notes

- Frontend dependency checks use `npm audit`.
- Backend dependency checks use `poetry run pip-audit`.
- React remains on version 18 and React Router remains on the 6.x line.
- Major backend framework migrations should be handled separately when they require behavior changes.
