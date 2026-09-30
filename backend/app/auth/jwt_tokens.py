from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import get_settings
from app.errors import InvalidTokenError


def _create(user_id: int, token_type: str, lifetime: timedelta) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + lifetime
    claims = {"sub": str(user_id), "type": token_type, "exp": expires}
    return jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int) -> str:
    minutes = get_settings().access_token_expire_minutes
    return _create(user_id, "access", timedelta(minutes=minutes))


def create_refresh_token(user_id: int) -> str:
    days = get_settings().refresh_token_expire_days
    return _create(user_id, "refresh", timedelta(days=days))


def decode_token(token: str, expected_type: str) -> int:
    settings = get_settings()
    try:
        claims = jwt.decode(token, settings.jwt_secret_key,
                            algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise InvalidTokenError("invalid or expired token") from exc
    if claims.get("type") != expected_type:
        raise InvalidTokenError("wrong token type")
    return int(claims["sub"])
