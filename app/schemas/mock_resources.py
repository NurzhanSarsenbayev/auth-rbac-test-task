from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int


class TaskCreateRequest(BaseModel):
    name: str


class TaskUpdateRequest(BaseModel):
    name: str


class TaskResponse(BaseModel):
    id: int
    name: str
    owner_id: int


class ReportResponse(BaseModel):
    id: int
    name: str
    owner_id: int