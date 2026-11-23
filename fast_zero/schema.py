from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fast_zero.models import TodoState


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


class Token(BaseModel):
    access_token: str
    token_type: str


class UserDB(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[PublicUser]


class FilterPage(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)

class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState

class TodoPublic(TodoSchema):
    id: int

class TodoList(BaseModel):
    todos: list[TodoPublic]

class FilterTodo(FilterPage):
    title: str | None = Field(None, min_length=3, max_length=20)
    description: str | None = Field(None, min_length=3, max_length=20)
    state: TodoState | None = Field(None, min_length=3, max_length=20)

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None