# Cheburek Shop

Cheburek Shop is a React storefront backed by a FastAPI API, PostgreSQL, MongoDB, and Redis.

## Stack

- Frontend: React 18, Vite, TypeScript, Redux Toolkit, SCSS modules, npm
- Backend: Python 3.12, FastAPI, Poetry, SQLAlchemy async, Alembic, Beanie, Redis, pytest
- Services: PostgreSQL 16, MongoDB 7, Redis 7
- Local orchestration: Docker Compose

## Local URLs

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

`setup.sh` creates local env files from examples, installs frontend dependencies when npm is available, and validates the Compose config. `scripts/dev.sh` starts the full stack with Docker Compose.

Run migrations after services are available:

```bash
./scripts/migrate.sh
```

Check the running stack:

```bash
./scripts/healthcheck.sh
```

## Environment

Copy examples if you want to edit values manually:

```bash
cp .env.example .env
cp front-end/.env.example front-end/.env
cp back-end/.env.example back-end/.env
```

Important root `.env` values:

- `FRONTEND_PORT`: frontend dev server port, default `5178`
- `BACKEND_PORT`: backend API port, default `8091`
- `POSTGRES_PORT`: host PostgreSQL port, default `55432`
- `MONGO_PORT`: host MongoDB port, default `27018`
- `REDIS_PORT`: host Redis port, default `6380`
- `VITE_API_BASE_URL`: browser API base URL, default `http://localhost:8091/api/v1`
- `CORS_ALLOWED_ORIGINS`: comma-separated frontend origins allowed by the API

Use stronger secrets before sharing an environment:

- `RESET_PASSWORD_TOKEN_SECRET`
- `VERIFICATION_TOKEN_SECRET`
- `SESSION_SECRET_KEY`

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
curl http://localhost:8091/health
```

## Troubleshooting

- `env file ... back-end/.env not found`: run `./setup.sh` or copy the example env files. Compose also has built-in safe defaults.
- Port already in use: update `.env`, `front-end/.env`, and `back-end/.env` so `FRONTEND_PORT`, `BACKEND_PORT`, `VITE_API_BASE_URL`, and `CORS_ALLOWED_ORIGINS` stay aligned.
- Frontend cannot reach the API: confirm `VITE_API_BASE_URL` points to the backend URL visible from the browser.
- CORS errors: add the frontend origin to `CORS_ALLOWED_ORIGINS`.
- Health check returns `degraded`: PostgreSQL, MongoDB, or Redis is not reachable from the backend container.
- Backend tests require PostgreSQL, MongoDB, and Redis. Start dependencies before running the full pytest suite.

## Dependency And Security Notes

- Frontend dependency checks use `npm audit`.
- Backend dependency checks use `poetry run pip-audit`.
- React remains on version 18 and React Router remains on the 6.x line.
- Major backend framework migrations should be handled separately when they require behavior changes.
