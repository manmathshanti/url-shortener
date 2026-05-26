from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.url import URL
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse, URLAnalyticsResponse
from app.services.cache_service import get_cached_url, set_cached_url, delete_cached_url
from app.utils.url_helper import generate_short_code, is_valid_url, build_short_url

settings = get_settings()


def format_url_response(url: URL) -> URLResponse:
    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=build_short_url(settings.base_url, url.short_code),
        total_clicks=url.total_clicks,
        is_active=url.is_active,
        created_at=url.created_at,
        last_accessed_at=url.last_accessed_at,
    )


def format_analytics_response(url: URL) -> URLAnalyticsResponse:
    return URLAnalyticsResponse(
        short_code=url.short_code,
        original_url=url.original_url,
        short_url=build_short_url(settings.base_url, url.short_code),
        total_clicks=url.total_clicks,
        created_at=url.created_at,
        last_accessed_at=url.last_accessed_at,
    )


async def create_short_url(url_data: URLCreate, user: User, db: AsyncSession) -> URLResponse:
    if not is_valid_url(url_data.original_url):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid URL format. Must include scheme (http/https).",
        )

    short_code = url_data.custom_alias or generate_short_code(settings.short_code_length)

    result = await db.execute(select(URL).where(URL.short_code == short_code))
    if result.scalar_one_or_none():
        if url_data.custom_alias:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom alias is already in use",
            )
        short_code = generate_short_code(settings.short_code_length)

    url = URL(
        original_url=url_data.original_url,
        short_code=short_code,
        user_id=user.id,
    )
    db.add(url)
    await db.commit()
    await db.refresh(url)

    await set_cached_url(short_code, url.original_url)
    return format_url_response(url)


async def resolve_short_url(short_code: str, db: AsyncSession) -> str:
    cached = await get_cached_url(short_code)
    if cached:
        await record_url_click(short_code, db)
        return cached

    result = await db.execute(
        select(URL).where(URL.short_code == short_code, URL.is_active == True)  # noqa: E712
    )
    url = result.scalar_one_or_none()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    await record_url_click(short_code, db)
    await set_cached_url(short_code, url.original_url)
    return url.original_url


async def record_url_click(short_code: str, db: AsyncSession) -> None:
    await db.execute(
        update(URL)
        .where(URL.short_code == short_code)
        .values(
            total_clicks=URL.total_clicks + 1,
            last_accessed_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()


async def fetch_user_urls(user: User, db: AsyncSession) -> list[URLResponse]:
    result = await db.execute(
        select(URL)
        .where(URL.user_id == user.id, URL.is_active == True)  # noqa: E712
        .order_by(URL.created_at.desc())
    )
    urls = result.scalars().all()
    return [format_url_response(u) for u in urls]


async def remove_user_url(short_code: str, user: User, db: AsyncSession) -> None:
    result = await db.execute(
        select(URL).where(
            URL.short_code == short_code,
            URL.user_id == user.id,
            URL.is_active == True,  # noqa: E712
        )
    )
    url = result.scalar_one_or_none()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    await db.execute(update(URL).where(URL.short_code == short_code).values(is_active=False))
    await db.commit()
    await delete_cached_url(short_code)


async def fetch_url_analytics(short_code: str, user: User, db: AsyncSession) -> URLAnalyticsResponse:
    result = await db.execute(
        select(URL).where(URL.short_code == short_code, URL.user_id == user.id)
    )
    url = result.scalar_one_or_none()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    return format_analytics_response(url)
