# Cheburek Shop Backend

FastAPI backend for the Cheburek Shop storefront.

## Requirements

- Python `3.12`
- Poetry
- PostgreSQL, MongoDB, and Redis for full local operation

Docker Compose from the repository root is the simplest way to run the required services.

## Environment

Create a local env file:

```bash
cp .env.example .env
```

Important variables:

- `APP_CONFIG__RUN__HOST`: API host, default `127.0.0.1`
- `APP_CONFIG__RUN__PORT`: API port, default `8091`
- `APP_CONFIG__DB__URL`: async PostgreSQL URL
- `APP_CONFIG__DB__TEST_URL`: async PostgreSQL test URL
- `APP_CONFIG__MONGO_DB__HOST`: MongoDB host
- `APP_CONFIG__MONGO_DB__PORT`: MongoDB port
- `APP_CONFIG__REDIS__HOST`: Redis host
- `APP_CONFIG__REDIS__PORT`: Redis port
- `APP_CONFIG__CORS__ALLOWED_ORIGINS`: comma-separated frontend origins
- `APP_CONFIG__ACCESS_TOKEN__RESET_PASSWORD_TOKEN_SECRET`: reset-token secret
- `APP_CONFIG__ACCESS_TOKEN__VERIFICATION_TOKEN_SECRET`: verification-token secret
- `APP_CONFIG__SESSION__SECRET_KEY`: session middleware secret

## Commands

Install:

```bash
poetry install
```

Run API:

```bash
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8091 --reload
```

Run migrations:

```bash
poetry run alembic upgrade head
```

Verify:

```bash
poetry run python -m compileall -q app migrations
poetry run pytest
poetry run pip-audit
```

Health check:

```bash
curl http://localhost:8091/health
```

## Docker Compose

From the repository root:

```bash
docker compose up -d postgres mongo redis fastapi
docker compose run --rm fastapi alembic upgrade head
```

Default API URLs:

- `http://localhost:8091/health`
- `http://localhost:8091/api/v1`

## Troubleshooting

- Settings validation fails: confirm required `APP_CONFIG__...` variables exist in `.env`.
- Health check is `degraded`: one of PostgreSQL, MongoDB, or Redis is not reachable.
- Tests fail to connect to databases: start dependencies with Docker Compose first.
- Browser CORS errors: make sure the frontend origin is listed in `APP_CONFIG__CORS__ALLOWED_ORIGINS`.

## Dependency And Security Notes

- Runtime dependencies are managed by Poetry and locked in `poetry.lock`.
- `pip-audit` is included for dependency vulnerability checks.
- `aioredis` is not required because the code uses `redis.asyncio`.
