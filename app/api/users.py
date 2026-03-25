from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UpdateUserRequest, UserResponse


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    if payload.email and payload.email != current_user.email:
        existing_email_user = db.scalar(
            select(User).where(
                User.email == payload.email,
                User.id != current_user.id,
            )
        )
        if existing_email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already taken.",
            )
        current_user.email = payload.email

    if payload.username and payload.username != current_user.username:
        existing_username_user = db.scalar(
            select(User).where(
                User.username == payload.username,
                User.id != current_user.id,
            )
        )
        if existing_username_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken.",
            )
        current_user.username = payload.username

    if payload.password:
        current_user.password_hash = hash_password(payload.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    current_user.is_deleted = True
    current_user.is_active = False

    db.add(current_user)
    db.commit()