import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class URLCreate(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if len(value) < 3 or len(value) > 20:
            raise ValueError("Custom alias must be between 3 and 20 characters")
        if not value.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Custom alias may only contain letters, numbers, hyphens, and underscores")
        return value


class URLResponse(BaseModel):
    id: uuid.UUID
    original_url: str
    short_code: str
    short_url: str
    total_clicks: int
    is_active: bool
    created_at: datetime
    last_accessed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class URLAnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    short_url: str
    total_clicks: int
    created_at: datetime
    last_accessed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
