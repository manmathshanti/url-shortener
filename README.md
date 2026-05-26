# URL Shortener

A FastAPI app for shortening links, managing them behind login, and tracking basic click analytics.

It includes:

- user registration and login with JWT auth
- short link creation with optional custom aliases
- a simple built-in web UI for normal use
- redirect handling with Redis caching
- per-link analytics like total clicks and last access time

## What’s in the app

- `POST /auth/register` to create an account
- `POST /auth/login` to get an access token
- `POST /urls` to create a short URL
- `GET /urls` to list your URLs
- `DELETE /urls/{short_code}` to deactivate one
- `GET /urls/{short_code}/analytics` to view stats for one link
- `GET /{short_code}` to redirect to the original URL
- `GET /health` for a simple health check

Swagger is available at `/docs`.

The app also serves a basic frontend:

- `/` main UI
- `/app` same UI on an alternate route

## Stack

- FastAPI
- SQLAlchemy async + `asyncpg`
- PostgreSQL
- Redis
- JWT auth with `python-jose`
- Alembic for migrations

## Project layout

```text
app/
├── main.py
├── config.py
├── database.py
├── exceptions/
├── models/
├── routers/
├── schemas/
├── services/
├── static/
└── utils/
tests/
```

## Local setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

This project reads settings from `.env`.

There is currently no `.env.example`, so either create your own `.env` or copy from an existing local setup and replace the secrets.

Important settings:

- `APP_NAME`
- `DEBUG`
- `BASE_URL`
- `TEST_MODE`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DB_SSLMODE`
- `AIVEN_DB_HOST`
- `AIVEN_DB_PORT`
- `AIVEN_DB_USER`
- `AIVEN_DB_PASSWORD`
- `AIVEN_DB_NAME`
- `AIVEN_DB_SSLMODE`
- `SECRET_KEY`
- `REDIS_URL`
- `REDIS_TTL`
- `SHORT_CODE_LENGTH`
- `RATE_LIMIT_PER_MINUTE`
- `DB_SCHEMA`

How database selection works:

- if `TEST_MODE=true`, the app uses the `DB_*` values
- if `TEST_MODE=false`, the app uses the `AIVEN_DB_*` values

### 4. Start the app

```bash
uvicorn app.main:app --reload
```

By default it runs on:

- `http://localhost:8000/` for the UI
- `http://localhost:8000/docs` for Swagger

## Docker

You can run the project with Docker Compose:

```bash
docker-compose up --build
```

That starts:

- the FastAPI app
- PostgreSQL
- Redis

The current `docker-compose.yml` is meant for local development.

## Notes about the current config

A couple of details are worth knowing before deployment:

- the app builds its database connection from `DB_*` or `AIVEN_DB_*` variables in `app/config.py`
- it does not currently read a single `DATABASE_URL` setting
- the Dockerfile currently starts Uvicorn on port `8000`, which is fine locally but usually needs adjustment for platforms like Render that inject `PORT`

## Running tests

```bash
pytest tests/ -v
```

The test suite uses SQLite, but the app’s default schema handling is PostgreSQL-oriented. If tests fail around schema creation, that is a project setup issue, not necessarily an app logic issue.

## Deploying

This project can be deployed to Render, but the cleanest setup is:

- one web service for the FastAPI app
- one Postgres instance
- one Redis-compatible key/value instance

Before deploying, make sure you:

- set a real production `BASE_URL`
- set a strong `SECRET_KEY`
- use the correct database host, port, username, password, and SSL mode
- rotate any credentials that were committed or shared during development

## A quick warning

If your `.env` contains real database passwords or JWT secrets, rotate them before pushing the project or deploying it anywhere public.
