# Dockerfile

# The builder image, used to build the virtual environment
FROM python:3.12.3-alpine3.20 as builder

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

# The runtime image
FROM python:3.12.3-alpine3.20 as runtime

ENV VIRTUAL_ENV=/backend/.venv \
    PATH="/backend/.venv/bin:$PATH"

# Copy virtual environment and application code from builder
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY . .

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]