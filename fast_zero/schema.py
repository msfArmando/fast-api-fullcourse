from pydantic import BaseModel, EmailStr


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

class UserDB(UserSchema):
    id: int