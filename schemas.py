from pydantic import BaseModel, EmailStr,constr,field_validator
from typing import Optional, List
from datetime import datetime
import enum,re

class Role(str, enum.Enum):
    manager = "manager"
    staff = "staff"
    guest = "guest"


class RegisterRequest(BaseModel):
    name: constr(min_length=1)
    email: EmailStr
    password: constr(min_length=6)
    role: Optional[Role] = Role.guest
    @field_validator("name")
    @classmethod
    def name_must_be_alphabets(cls, v):
        if not re.match(r'^[A-Za-z\s]+$', v):
            raise ValueError("Name must contain only alphabets")
        return v

    @field_validator("email")
    @classmethod
    def email_must_be_gmail(cls, v):
        if not v.endswith("@gmail.com"):
            raise ValueError("Email must be a Gmail address (must end with @gmail.com)")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must include at least one number")
        if not re.search(r'[@$!#%*?&]', v):
            raise ValueError("Password must include at least one special character (@, $, !, #, %, *, ?, &)")
        return v

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
    staff_id: int

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
        from_attributes = True


class InventoryBase(BaseModel):
    item_name: str
    quantity: int
    unit: str
    threshold: int


class InventoryItemCreate(InventoryBase):
    pass

class InventoryItemUpdate(BaseModel):
    quantity: int

class InventoryOut(InventoryBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


