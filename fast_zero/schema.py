from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class ReadRoot(BaseModel):
    message: str


class UserSchema(BaseModel):
    email: EmailStr
    username: str
    password: str


class PublicUser(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime
    update_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserDB(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[PublicUser]
