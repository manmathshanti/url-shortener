from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(include_in_schema=False)

index_file = Path(__file__).resolve().parent.parent / "static" / "index.html"


@router.get("/")
async def ui_home():
    return FileResponse(index_file)


@router.get("/app")
async def ui_app():
    return FileResponse(index_file)
