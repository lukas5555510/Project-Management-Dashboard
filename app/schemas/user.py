from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    login: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str