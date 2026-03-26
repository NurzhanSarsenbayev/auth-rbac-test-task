from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.db.session import get_db
from app.models.user import User
from app.services.permission_service import (
    can_access_object,
    get_user_permission_for_resource,
)

router = APIRouter(prefix="/mock", tags=["mock-resources"])


projects_data = [
    {"id": 1, "name": "Project Alpha", "owner_id": 1},
    {"id": 2, "name": "Project Beta", "owner_id": 2},
]

tasks_data = [
    {"id": 1, "name": "Task One", "owner_id": 1},
    {"id": 2, "name": "Task Two", "owner_id": 2},
]

reports_data = [
    {"id": 1, "name": "Report One", "owner_id": 1},
    {"id": 2, "name": "Report Two", "owner_id": 2},
]


def get_object_or_404(items: list[dict], object_id: int) -> dict:
    for item in items:
        if item["id"] == object_id:
            return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Object not found.",
    )


@router.get("/projects")
def list_projects(
    current_user: User = Depends(require_permission("projects", "read")),
) -> list[dict]:
    return projects_data


@router.get("/projects/{project_id}")
def get_project(
    project_id: int,
    current_user: User = Depends(require_permission("projects", "read")),
) -> dict:
    return get_object_or_404(projects_data, project_id)


@router.get("/tasks")
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("tasks", "read")),
) -> list[dict]:
    permission = get_user_permission_for_resource(db, current_user, "tasks")
    if permission and permission.scope == "all":
        return tasks_data

    return [task for task in tasks_data if task["owner_id"] == current_user.id]


@router.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("tasks", "read")),
) -> dict:
    task = get_object_or_404(tasks_data, task_id)
    permission = get_user_permission_for_resource(db, current_user, "tasks")

    if not can_access_object(permission, task["owner_id"], current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this task.",
        )

    return task


@router.post("/tasks")
def create_task(
    payload: dict,
    current_user: User = Depends(require_permission("tasks", "create")),
) -> dict:
    new_task = {
        "id": len(tasks_data) + 1,
        "name": payload.get("name", "New Task"),
        "owner_id": current_user.id,
    }
    tasks_data.append(new_task)
    return new_task


@router.patch("/tasks/{task_id}")
def update_task(
    task_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("tasks", "update")),
) -> dict:
    task = get_object_or_404(tasks_data, task_id)
    permission = get_user_permission_for_resource(db, current_user, "tasks")

    if not can_access_object(permission, task["owner_id"], current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this task.",
        )

    task["name"] = payload.get("name", task["name"])
    return task


@router.get("/reports")
def list_reports(
    current_user: User = Depends(require_permission("reports", "read")),
) -> list[dict]:
    return reports_data