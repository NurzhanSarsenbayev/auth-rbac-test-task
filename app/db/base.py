from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models import Resource, Role, RolePermission, User, UserRole  # noqa: E402, F401