from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.resource import Resource
from app.models.role import Role, UserRole
from app.models.role_permission import RolePermission
from app.models.user import User
from app.core.security import hash_password


engine = create_engine(settings.test_database_url)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        admin_role = Role(name="admin")
        user_role = Role(name="user")
        db.add_all([admin_role, user_role])
        db.flush()

        projects = Resource(name="projects", description="Project resource")
        tasks = Resource(name="tasks", description="Task resource")
        reports = Resource(name="reports", description="Report resource")
        db.add_all([projects, tasks, reports])
        db.flush()

        admin_user = User(
            email="admin@example.com",
            username="admin",
            password_hash=hash_password("admin123"),
            is_active=True,
            is_deleted=False,
        )
        regular_user = User(
            email="user@example.com",
            username="user",
            password_hash=hash_password("user123"),
            is_active=True,
            is_deleted=False,
        )
        db.add_all([admin_user, regular_user])
        db.flush()

        db.add_all(
            [
                UserRole(user_id=admin_user.id, role_id=admin_role.id),
                UserRole(user_id=regular_user.id, role_id=user_role.id),
            ]
        )

        db.add_all(
            [
                RolePermission(
                    role_id=admin_role.id,
                    resource_id=projects.id,
                    can_read=True,
                    can_create=True,
                    can_update=True,
                    can_delete=True,
                    scope="all",
                ),
                RolePermission(
                    role_id=admin_role.id,
                    resource_id=tasks.id,
                    can_read=True,
                    can_create=True,
                    can_update=True,
                    can_delete=True,
                    scope="all",
                ),
                RolePermission(
                    role_id=admin_role.id,
                    resource_id=reports.id,
                    can_read=True,
                    can_create=True,
                    can_update=True,
                    can_delete=True,
                    scope="all",
                ),
                RolePermission(
                    role_id=user_role.id,
                    resource_id=projects.id,
                    can_read=True,
                    can_create=False,
                    can_update=False,
                    can_delete=False,
                    scope="all",
                ),
                RolePermission(
                    role_id=user_role.id,
                    resource_id=tasks.id,
                    can_read=True,
                    can_create=True,
                    can_update=True,
                    can_delete=False,
                    scope="own",
                ),
                RolePermission(
                    role_id=user_role.id,
                    resource_id=reports.id,
                    can_read=False,
                    can_create=False,
                    can_update=False,
                    can_delete=False,
                    scope="own",
                ),
            ]
        )

        db.commit()
        yield
    finally:
        db.close()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]