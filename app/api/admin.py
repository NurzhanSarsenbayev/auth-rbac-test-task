from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.schemas.permission import (
    PermissionResponse,
    RoleResponse,
    UpdatePermissionRequest,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[Role]:
    roles = db.scalars(select(Role).order_by(Role.id)).all()
    return list(roles)


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[RolePermission]:
    permissions = db.scalars(
        select(RolePermission).order_by(RolePermission.id)
    ).all()
    return list(permissions)


@router.patch("/permissions/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    payload: UpdatePermissionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> RolePermission:
    permission = db.scalar(
        select(RolePermission).where(RolePermission.id == permission_id)
    )

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found.",
        )

    if payload.can_read is not None:
        permission.can_read = payload.can_read
    if payload.can_create is not None:
        permission.can_create = payload.can_create
    if payload.can_update is not None:
        permission.can_update = payload.can_update
    if payload.can_delete is not None:
        permission.can_delete = payload.can_delete
    if payload.scope is not None:
        permission.scope = payload.scope

    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission