from sqlalchemy.orm import Session
import models, schemas

# ---- Rooms ----
def get_rooms(db: Session):
    return db.query(models.Room).all()

def create_room(db: Session, room: schemas.RoomCreate):
    db_room = models.Room(room_number=room.room_number, status=room.status)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def update_room_status(db: Session, room_id: int, status: str):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if db_room:
        db_room.status = status
        db.commit()
        db.refresh(db_room)
    return db_room

# ---- Bookings ----
def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    # mark room as booked
    update_room_status(db, booking.room_id, "booked")
    return db_booking

def checkin_booking(db: Session, booking_id: int):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if booking:
        booking.status = "checked_in"
        update_room_status(db, booking.room_id, "occupied")
        db.commit()
        db.refresh(booking)
    return booking

def checkout_booking(db: Session, booking_id: int):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if booking:
        booking.status = "checked_out"
        update_room_status(db, booking.room_id, "cleaning")
        db.commit()
        db.refresh(booking)
    return booking

# ---- Housekeeping ----
def create_housekeeping(db: Session, housekeeping: schemas.HousekeepingCreate):
    db_hk = models.Housekeeping(**housekeeping.dict())
    db.add(db_hk)
    db.commit()
    db.refresh(db_hk)
    return db_hk

def update_housekeeping(db: Session, hk_id: int, status: str):
    db_hk = db.query(models.Housekeeping).filter(models.Housekeeping.id == hk_id).first()
    if db_hk:
        db_hk.status = status
        if status == "completed":
            update_room_status(db, db_hk.room_id, "available")
        db.commit()
        db.refresh(db_hk)
    return db_hk
