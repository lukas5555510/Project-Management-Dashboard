from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    login: str
    email: EmailStr
    password: str
    repeat_password: str


class UserLogin(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str