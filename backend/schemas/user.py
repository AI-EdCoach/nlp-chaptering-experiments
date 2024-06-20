from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


# Shared properties
class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class UserReadSchema(UserBaseSchema):
    id: int


# Properties to receive via API on creation
class UserCreateSchema(UserBaseSchema):
    password: str


# Properties to receive via API on update
class UserUpdateSchema(UserBaseSchema):
    password: str | None = None
