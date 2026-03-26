from pydantic import BaseModel


# POST /auth
class UserCreate(BaseModel):
    login: str
    password: str
    repeat_password: str

# POST /login
class UserLogin(BaseModel):
    login: str
    password: str