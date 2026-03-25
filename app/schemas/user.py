from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_deleted: bool
    created_at: datetime

    model_config = {"from_attributes": True}
