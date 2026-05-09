# Cheburek Shop

Cheburek Shop is a React storefront backed by a FastAPI API, PostgreSQL, MongoDB, and Redis.

## Stack

- Frontend: React 18, Vite, TypeScript, Redux Toolkit, SCSS modules, npm
- Backend: Python 3.12, FastAPI, Poetry, SQLAlchemy async, Alembic, Beanie, Redis, pytest
- Services: PostgreSQL 16, MongoDB 7, Redis 7
- Local orchestration: Docker Compose

## Local URLs

Preferred local-domain URLs:

| Service | Default URL |
| --- | --- |
| Frontend | `http://app.local.cheburek-shop.com:5178` |
| Admin portal | `http://admin.local.cheburek-shop.com:5178` |
| Backend API | `http://api.local.cheburek-shop.com:8091/api/v1` |
| Backend health | `http://api.local.cheburek-shop.com:8091/health` |

Localhost fallback URLs:

| Service | Default URL |
| --- | --- |
| Frontend | `http://localhost:5178` |
| Backend API | `http://localhost:8091/api/v1` |
| Backend health | `http://localhost:8091/health` |
| PostgreSQL host port | `55432` |
| MongoDB host port | `27018` |
| Redis host port | `6380` |

Ports are intentionally offset from common defaults. Override them in `.env` if needed.

## Quick Start

```bash
./setup.sh
./scripts/dev.sh
```

`setup.sh` creates local env files, generates local-only secrets, installs frontend dependencies when npm is available, validates Docker Compose, and offers to add these hostnames to `/etc/hosts`:

```text
127.0.0.1 app.local.cheburek-shop.com api.local.cheburek-shop.com admin.local.cheburek-shop.com
```

If you do not want the script to touch `/etc/hosts`, run:

```bash
./setup.sh --skip-hosts
```

Then add the hosts entry manually or use the storefront localhost fallback URL.

`scripts/dev.sh` runs setup when needed, starts PostgreSQL, MongoDB, and Redis, runs migrations, seeds the product catalog idempotently, bootstraps the local admin user, and then starts the API and frontend.

Run migrations and the idempotent product seed after services are available:

```bash
./scripts/migrate.sh
```

The product seed creates missing seed products and updates known seed product fields by English product name. It does not delete unrelated products, carts, or orders. A destructive seed reset is available only as an explicit local maintenance action:

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
- `FRONTEND_PORT`: frontend dev server port
- `BACKEND_PORT`: backend API port
- `POSTGRES_PORT`: host PostgreSQL port
- `MONGO_PORT`: host MongoDB port
- `REDIS_PORT`: host Redis port
- `VITE_API_BASE_URL`: browser API base URL
- `CORS_ALLOWED_ORIGINS`: comma-separated frontend origins allowed by the API
- `POSTGRES_PASSWORD`: generated local database password
- `RESET_PASSWORD_TOKEN_SECRET`: generated local reset-token secret
- `VERIFICATION_TOKEN_SECRET`: generated local verification-token secret
- `SESSION_SECRET_KEY`: generated local session secret
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
docker compose up -d postgres mongo redis fastapi
curl http://api.local.cheburek-shop.com:8091/health
```

Admin and seed helpers:

```bash
docker compose run --rm fastapi python -m app.actions.seed_products
docker compose run --rm fastapi python -m app.actions.create_super_user
```

## Troubleshooting

- Compose reports a missing secret: run `./setup.sh` before starting services.
- Local-domain URLs do not resolve: add the hosts entry shown by `./setup.sh`, then retry.
- Admin portal does not open: confirm `admin.local.cheburek-shop.com` is in `/etc/hosts` and `VITE_DEV_ALLOWED_HOSTS`.
- Port already in use: update `.env`, `front-end/.env`, and `back-end/.env` so ports, `VITE_API_BASE_URL`, and `CORS_ALLOWED_ORIGINS` stay aligned.
- Frontend cannot reach the API: confirm `VITE_API_BASE_URL` points to the backend URL visible from the browser.
- Storefront works on localhost but local domains fail: rerun `./setup.sh` in a terminal and accept or manually add the printed hosts entry.
- CORS errors: add the frontend origin to `CORS_ALLOWED_ORIGINS`.
- Health check returns `degraded`: PostgreSQL, MongoDB, or Redis is not reachable from the backend container.
- Backend tests require PostgreSQL, MongoDB, and Redis. Start dependencies before running the full pytest suite.
- After rotating local secrets, reset local volumes if database authentication no longer works.
- Admin login fails after rotating secrets: rerun `docker compose run --rm fastapi python -m app.actions.create_super_user` so the local admin password matches the generated env value.

## Dependency And Security Notes

- Frontend dependency checks use `npm audit`.
- Backend dependency checks use `poetry run pip-audit`.
- React remains on version 18 and React Router remains on the 6.x line.
- Major backend framework migrations should be handled separately when they require behavior changes.
