import secrets
import string
from typing import Optional

import validators as url_validators

BASE62_CHARS = string.ascii_letters + string.digits


def generate_short_code(length: int = 7) -> str:
    return "".join(secrets.choice(BASE62_CHARS) for _ in range(length))


def is_valid_url(url: str) -> bool:
    return bool(url_validators.url(url))


def build_short_url(base_url: str, short_code: str) -> str:
    return f"{base_url.rstrip('/')}/{short_code}"
