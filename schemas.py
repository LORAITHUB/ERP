from pydantic import BaseModel, EmailStr,constr
from typing import Optional, List
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


class TableResponse(BaseModel):
    id: int
    table_number: int
    capacity: int
    status: str

    model_config = {
        "from_attributes": True
    }

class CreateTable(BaseModel):
    table_number: int
    capacity: int
    status: str



class CreateReservation(BaseModel):
    user_id: int
    table_id: int
    reservation_time: datetime

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    table_id: int
    reservation_time: datetime
    status: str

    model_config = {
        "from_attributes": True
    }


class CreateMenuItem(BaseModel):
    name: str
    price: float
    availability: str
    category: str

class MenuItemResponse(BaseModel):
    id: int
    name: str
    price: float
    availability: str
    category: str

    model_config = {
        "from_attributes": True
    }

class CreateOrderItem(BaseModel):
    menu_item_id: int
    quantity: int
    price: float

class CreateOrder(BaseModel):
    table_id: int
    staff_id: int
    items: List[CreateOrderItem]

class OrderResponse(BaseModel):
    id: int
    table_id: int
    staff_id: int
    total_price: float
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UpdateOrderStatus(BaseModel):
    status: str


class BillingBase(BaseModel):
    booking_id: Optional[int] = None
    order_id: Optional[int] = None
    total_amount: float
    
class BillingCreate(BillingBase):
    pass

class BillingOut(BillingBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

