from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func,Enum, Numeric, TIMESTAMP,Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
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


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, nullable=False,index=True)
    status = Column(String, default="available")  

    bookings = relationship("Booking", back_populates="room")
    housekeeping = relationship("Housekeeping", back_populates="room")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    check_in = Column(TIMESTAMP)
    check_out = Column(TIMESTAMP)
    status = Column(String, default="booked")  

    room = relationship("Room", back_populates="bookings")


class Housekeeping(Base):
    __tablename__ = "housekeeping"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    status = Column(String, default="pending")  

    room = relationship("Room", back_populates="housekeeping")


class TableStatus(enum.Enum):
    available = "available"
    reserved = "reserved"
    occupied = "occupied"

class ReservationStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class OrderStatus(enum.Enum):
    pending = "pending"
    served = "served"
    billed = "billed"

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(Enum(TableStatus), default=TableStatus.available)

    reservations = relationship("Reservation", back_populates="table")
    orders = relationship("Order", back_populates="table")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    reservation_time = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.pending)

    table = relationship("Table", back_populates="reservations")

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    availability = Column(String(50), default="available")
    category = Column(String(50), nullable=False)

    order_items = relationship("OrderItem", back_populates="menu_item")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    staff_id = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), default=0.00)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    table = relationship("Table", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")


class Billing(Base):
    __tablename__ = "billing"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, nullable=True)
    order_id = Column(Integer, nullable=True)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=False)
    threshold = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



















'''
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
    price = Column(int, nullable=False)

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
'''