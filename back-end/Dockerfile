FROM python:3.12.3-alpine3.20 AS builder

# Install build dependencies and poetry
RUN apk add --no-cache gcc g++ musl-dev libffi-dev unixodbc-dev postgresql-dev
RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /backend

COPY poetry.lock pyproject.toml ./

# Creating README.md instead of copying
RUN touch README.md

# Install project dependencies
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

FROM python:3.12.3-alpine3.20 AS runtime

ENV VIRTUAL_ENV=/backend/.venv \
    PATH="/backend/.venv/bin:$PATH" \
    APP_CONFIG__RUN__HOST=0.0.0.0 \
    APP_CONFIG__RUN__PORT=8091

WORKDIR /backend

# Copy only necessary files from builder
COPY --from=builder /backend/.venv /backend/.venv
COPY . .

# Set the working directory to where the app folder is located
WORKDIR /backend

EXPOSE 8091

CMD ["sh", "-c", "uvicorn app.main:app --host ${APP_CONFIG__RUN__HOST:-0.0.0.0} --port ${APP_CONFIG__RUN__PORT:-8091} --reload"]
