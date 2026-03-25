from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.resource import Resource
from app.models.role import Role, UserRole
from app.models.role_permission import RolePermission
from app.models.user import User


def get_or_create_role(name: str, db) -> Role:
    role = db.scalar(select(Role).where(Role.name == name))
    if role:
        return role

    role = Role(name=name)
    db.add(role)
    db.flush()
    return role


def get_or_create_resource(name: str, description: str, db) -> Resource:
    resource = db.scalar(select(Resource).where(Resource.name == name))
    if resource:
        return resource

    resource = Resource(name=name, description=description)
    db.add(resource)
    db.flush()
    return resource


def get_or_create_user(email: str, username: str, password: str, db) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user:
        return user

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
        is_active=True,
        is_deleted=False,
    )
    db.add(user)
    db.flush()
    return user


def assign_role(user: User, role: Role, db) -> None:
    existing = db.scalar(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
    )
    if existing:
        return

    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.flush()


def get_or_create_permission(
    role: Role,
    resource: Resource,
    can_read: bool,
    can_create: bool,
    can_update: bool,
    can_delete: bool,
    scope: str,
    db,
) -> None:
    existing = db.scalar(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.resource_id == resource.id,
        )
    )
    if existing:
        return

    permission = RolePermission(
        role_id=role.id,
        resource_id=resource.id,
        can_read=can_read,
        can_create=can_create,
        can_update=can_update,
        can_delete=can_delete,
        scope=scope,
    )
    db.add(permission)
    db.flush()


def seed() -> None:
    db = SessionLocal()
    try:
        admin_role = get_or_create_role("admin", db)
        user_role = get_or_create_role("user", db)

        projects = get_or_create_resource("projects", "Project resource", db)
        tasks = get_or_create_resource("tasks", "Task resource", db)
        reports = get_or_create_resource("reports", "Report resource", db)

        admin_user = get_or_create_user(
            email="admin@example.com",
            username="admin",
            password="admin123",
            db=db,
        )
        regular_user = get_or_create_user(
            email="user@example.com",
            username="user",
            password="user123",
            db=db,
        )

        assign_role(admin_user, admin_role, db)
        assign_role(regular_user, user_role, db)

        for resource in (projects, tasks, reports):
            get_or_create_permission(
                role=admin_role,
                resource=resource,
                can_read=True,
                can_create=True,
                can_update=True,
                can_delete=True,
                scope="all",
                db=db,
            )

        get_or_create_permission(
            role=user_role,
            resource=projects,
            can_read=True,
            can_create=False,
            can_update=False,
            can_delete=False,
            scope="all",
            db=db,
        )
        get_or_create_permission(
            role=user_role,
            resource=tasks,
            can_read=True,
            can_create=True,
            can_update=True,
            can_delete=False,
            scope="own",
            db=db,
        )
        get_or_create_permission(
            role=user_role,
            resource=reports,
            can_read=False,
            can_create=False,
            can_update=False,
            can_delete=False,
            scope="own",
            db=db,
        )

        db.commit()
        print("Seed completed successfully.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()