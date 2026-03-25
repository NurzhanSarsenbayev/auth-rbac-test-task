from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class PermissionResponse(BaseModel):
    id: int
    role_id: int
    resource_id: int
    can_read: bool
    can_create: bool
    can_update: bool
    can_delete: bool
    scope: str

    model_config = {"from_attributes": True}


class UpdatePermissionRequest(BaseModel):
    can_read: bool | None = None
    can_create: bool | None = None
    can_update: bool | None = None
    can_delete: bool | None = None
    scope: str | None = None