# URL Shortener API

A production-ready URL shortener service (Bitly-like) built with FastAPI, PostgreSQL, and Redis.

## Features

- **JWT Authentication** — register, login, protected endpoints
- **URL Management** — create, list, delete short URLs with optional custom aliases
- **Analytics** — click counts, creation timestamps, last-accessed timestamps
- **Redis Caching** — fast redirect resolution without hitting the database
- **Rate Limiting** — 60 requests/minute per IP (configurable)
- **Async APIs** — fully async with SQLAlchemy 2 + asyncpg
- **Docker** — one-command setup with `docker-compose up`
- **Alembic** — database migration support
- **Swagger UI** — interactive docs at `/docs`

## Project Structure

```
app/
├── main.py              # FastAPI app, middleware, lifespan
├── config.py            # Settings via pydantic-settings
├── database.py          # Async SQLAlchemy engine & session
├── models/
│   ├── user.py          # User ORM model
│   └── url.py           # URL ORM model
├── schemas/
│   ├── user.py          # Pydantic request/response schemas
│   └── url.py           # Pydantic request/response schemas
├── services/
│   ├── auth_service.py  # Registration, login, JWT validation
│   ├── url_service.py   # URL CRUD, redirect, analytics
│   └── cache_service.py # Redis get/set/delete helpers
├── routers/
│   ├── auth.py          # POST /auth/register, POST /auth/login
│   ├── urls.py          # POST/GET /urls, DELETE/GET /urls/{code}
│   └── redirect.py      # GET /{short_code} → 302 redirect
├── utils/
│   ├── security.py      # Password hashing, JWT encode/decode
│   ├── url_helper.py    # Short code generation, URL validation
│   └── validators.py    # Regex validators
└── exceptions/
    └── handlers.py      # Global exception handlers
```

## Quick Start

### With Docker (recommended)

```bash
cp .env.example .env          # edit SECRET_KEY at minimum
docker-compose up --build
```

API is available at `http://localhost:8000`. Swagger UI at `http://localhost:8000/docs`.

### Local development

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # fill in DATABASE_URL, REDIS_URL, SECRET_KEY
uvicorn app.main:app --reload
```

Run database migrations (after initial setup):

```bash
alembic upgrade head
```

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Register a new user |
| POST | `/auth/login` | No | Login, returns JWT token |
| POST | `/urls` | Yes | Create a short URL |
| GET | `/urls` | Yes | List your short URLs |
| DELETE | `/urls/{code}` | Yes | Delete a short URL |
| GET | `/urls/{code}/analytics` | Yes | URL click analytics |
| GET | `/{code}` | No | Redirect to original URL |
| GET | `/health` | No | Health check |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgres://... | Async PostgreSQL connection string |
| `REDIS_URL` | redis://localhost:6379 | Redis connection string |
| `SECRET_KEY` | *(required)* | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token TTL |
| `BASE_URL` | http://localhost:8000 | Used to build short URLs |
| `SHORT_CODE_LENGTH` | 7 | Length of auto-generated codes |
| `RATE_LIMIT_PER_MINUTE` | 60 | Requests per IP per minute |
| `REDIS_TTL` | 3600 | Cache TTL in seconds |

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Tests use SQLite in-memory via `aiosqlite` — no PostgreSQL or Redis required.
