from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import UserRole
from app.models.resource import Resource
from app.models.role_permission import RolePermission
from app.models.user import User


def get_user_permission_for_resource(
    db: Session,
    user: User,
    resource_name: str,
) -> RolePermission | None:
    resource = db.scalar(
        select(Resource).where(Resource.name == resource_name)
    )
    if not resource:
        return None

    permission = db.scalar(
        select(RolePermission)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(
            UserRole.user_id == user.id,
            RolePermission.resource_id == resource.id,
        )
    )
    return permission


def has_permission(
    permission: RolePermission | None,
    action: str,
) -> bool:
    if permission is None:
        return False

    action_map = {
        "read": permission.can_read,
        "create": permission.can_create,
        "update": permission.can_update,
        "delete": permission.can_delete,
    }

    return action_map.get(action, False)