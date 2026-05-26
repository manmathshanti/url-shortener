from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse, URLAnalyticsResponse
from app.services.auth_service import get_current_user
from app.services.url_service import (
    create_short_url,
    fetch_user_urls,
    remove_user_url,
    fetch_url_analytics,
)

router = APIRouter(prefix="/urls", tags=["URLs"])


@router.post(
    "",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new short URL",
)
async def create_url(
    request: Request,
    url_data: URLCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_short_url(url_data, user, db)


@router.get(
    "",
    response_model=list[URLResponse],
    summary="List all short URLs for the authenticated user",
)
async def list_urls(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await fetch_user_urls(user, db)


@router.delete(
    "/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a short URL",
)
async def delete_url(
    short_code: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await remove_user_url(short_code, user, db)


@router.get(
    "/{short_code}/analytics",
    response_model=URLAnalyticsResponse,
    summary="Get analytics for a specific short URL",
)
async def get_analytics(
    short_code: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await fetch_url_analytics(short_code, user, db)
