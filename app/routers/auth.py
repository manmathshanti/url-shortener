from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(user_data, db)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and receive a JWT access token",
)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    access_token = await login_user(credentials.email, credentials.password, db)
    return Token(access_token=access_token)
