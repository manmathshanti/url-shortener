import re

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]{3,50}$")
SHORT_CODE_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def is_valid_username(username: str) -> bool:
    return bool(USERNAME_RE.match(username))


def is_valid_short_code(code: str) -> bool:
    return bool(SHORT_CODE_RE.match(code))
