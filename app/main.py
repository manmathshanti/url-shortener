from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import get_settings
from app.database import create_tables
from app.exceptions.handlers import register_exception_handlers
from app.routers import auth, urls, redirect
from app.services.cache_service import close_redis_connection

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await close_redis_connection()


app = FastAPI(
    title=settings.app_name,
    description=(
        "A Bitly-like URL shortener API with JWT authentication, "
        "Redis caching, click analytics, and rate limiting."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

@app.get("/health", tags=["Health"], summary="Service health check")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}


app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(redirect.router)  # must be last — /{short_code} would swallow earlier routes
