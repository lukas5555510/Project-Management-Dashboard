from pydantic import BaseModel, Field, EmailStr

# POST /auth
class UserCreate(BaseModel):
    login: str
    email: EmailStr
    password: str
    repeat_password: str

# POST /login
class UserLogin(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token for authentication")
    token_type: str = Field(default="bearer", description="Token type, usually 'bearer'")