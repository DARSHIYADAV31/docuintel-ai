from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt_tokens import create_access_token, create_refresh_token, decode_token
from app.auth.passwords import hash_password, verify_password
from app.auth.schemas import Credentials, RefreshRequest, TokenPair
from app.db.repositories import user_repo
from app.db.session import get_db
from app.errors import InvalidTokenError
from app.logging_setup import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
log = get_logger(__name__)


def _token_pair(user_id: int) -> TokenPair:
    return TokenPair(access_token=create_access_token(user_id),
                     refresh_token=create_refresh_token(user_id))


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: Credentials, db: Session = Depends(get_db)) -> TokenPair:
    if user_repo.get_by_username(db, body.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    user = user_repo.create_user(db, body.username, hash_password(body.password))
    log.info("user registered id=%d", user.id)
    return _token_pair(user.id)


@router.post("/login")
def login(body: Credentials, db: Session = Depends(get_db)) -> TokenPair:
    user = user_repo.get_by_username(db, body.username)
    if not user or not verify_password(body.password, user.password_hash):
        log.warning("failed login attempt")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return _token_pair(user.id)


@router.post("/refresh")
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        user_id = decode_token(body.refresh_token, "refresh")
    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    if user_repo.get_by_id(db, user_id) is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return _token_pair(user_id)
