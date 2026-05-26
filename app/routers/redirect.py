from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.url_service import resolve_short_url

router = APIRouter(tags=["Redirect"])


@router.get(
    "/{short_code}",
    status_code=status.HTTP_302_FOUND,
    summary="Redirect short URL to the original URL",
    response_class=RedirectResponse,
)
async def redirect_to_original(
    request: Request,
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    original_url = await resolve_short_url(short_code, db)
    return RedirectResponse(url=original_url, status_code=status.HTTP_302_FOUND)
