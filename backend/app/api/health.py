from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.db.models import User

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict:
    return {"id": user.id, "username": user.username, "role": user.role}
