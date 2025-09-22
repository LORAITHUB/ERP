from sqlalchemy import Column, Integer, String, Enum
from database import Base
import enum

class RoleEnum(str, enum.Enum):
    manager = "manager"
    staff = "staff"
    guest = "guest"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    email = Column(String(320), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.guest, nullable=False)

class RoomType(enum.Enum):
    single = "single"
    double = "double"
    suite = "suite"

class RoomStatus(enum.Enum):
    available = "available"
    occupied = "occupied"
    cleaning = "cleaning"

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, nullable=False, unique=True)
    type = Column(Enum(RoomType), nullable=False)
    status = Column(Enum(RoomStatus), nullable=False)
    price = Column(Float, nullable=False)

class BookingStatus(enum.Enum):
    booked = "booked"
    checked_in = "checked_in"
    checked_out = "checked_out"
    cancelled = "cancelled"

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), nullable=False)

class HousekeepingStatus(enum.Enum):
    pending = "pending"
    completed = "completed"

class Housekeeping(Base):
    __tablename__ = "housekeeping"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    staff_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(HousekeepingStatus), nullable=False)
    assigned_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)

class OrderStatus(enum.Enum):
    pending = "pending"
    served = "served"
    billed = "billed"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer)  # If needed, can add ForeignKey
    staff_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    status = Column(Enum(OrderStatus), nullable=False)
    created_at = Column(DateTime, nullable=False)

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String, nullable=False)
    threshold = Column(Integer, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class Billing(Base):
    __tablename__ = "billing"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
