from pydantic import BaseModel, EmailStr,constr
from typing import Optional
from datetime import datetime
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

#naveetask
class RoomBase(BaseModel):
    room_number: str
    status: Optional[str] = "available"

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    class Config:
        from_attributes = True

class RoomStatusUpdate(BaseModel):
    status: str        


class BookingBase(BaseModel):
    room_id: int
    check_in: datetime
    check_out: datetime
    status: Optional[str] = "booked"

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    class Config:
        from_attributes = True


class HousekeepingBase(BaseModel):
    room_id: int
    status: Optional[str] = "pending"

class HousekeepingCreate(HousekeepingBase):
    pass

class Housekeeping(HousekeepingBase):
    id: int
    class Config:
        from_attributes = True
    
