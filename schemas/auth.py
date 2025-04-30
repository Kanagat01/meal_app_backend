from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    full_name: str
    username: str
    password: str


class UserLoginSchema(BaseModel):
    username: str
    password: str
