from pydantic import BaseModel, EmailStr,constr
from typing import Optional
import enum

class Role(str, enum.Enum):
    manager = "manager"
    staff = "staff"
    guest = "guest"


class RegisterRequest(BaseModel):
    name: constr(min_length=1)
    email: EmailStr
    password: constr(min_length=6)
    role: Optional[Role] = Role.guest

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
