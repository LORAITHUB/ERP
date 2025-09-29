from sqlalchemy.orm import Session
import schemas,models



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

def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

   
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


from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas

# ✅ Create housekeeping task
def create_housekeeping(db: Session, housekeeping: schemas.HousekeepingCreate):
    # check if room exists
    room = db.query(models.Room).filter(models.Room.id == housekeeping.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {housekeeping.room_id} not found")

    # check if staff exists
    staff = db.query(models.User).filter(models.User.id == housekeeping.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff {housekeeping.staff_id} not found")

    # ✅ only allow staff role
    if staff.role != models.RoleEnum.staff:
        raise HTTPException(status_code=400, detail=f"User {housekeeping.staff_id} is not a staff member")

    # create housekeeping task
    db_hk = models.Housekeeping(
        room_id=housekeeping.room_id,
        staff_id=housekeeping.staff_id,
        status=housekeeping.status
    )
    db.add(db_hk)
    db.commit()
    db.refresh(db_hk)
    return db_hk


# ✅ Update housekeeping status
def update_housekeeping(db: Session, hk_id: int, status: str):
    db_hk = db.query(models.Housekeeping).filter(models.Housekeeping.id == hk_id).first()
    if not db_hk:
        raise HTTPException(status_code=404, detail=f"Housekeeping task {hk_id} not found")

    db_hk.status = status

    # if housekeeping is completed → mark room available
    if status == "completed":
        room = db.query(models.Room).filter(models.Room.id == db_hk.room_id).first()
        if room:
            room.status = "available"

    db.commit()
    db.refresh(db_hk)
    return db_hk



def get_inventory_items(db: Session):
    return db.query(models.Inventory).all()

def create_inventory_item(db: Session, item: schemas.InventoryItemCreate):
    
    db_item = models.Inventory(**item.dict())
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_inventory_quantity(db: Session, item_id: int, quantity: int):
    
    db_item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    
    if db_item:
        db_item.quantity = quantity
        db.commit()
        db.refresh(db_item)
    return db_item

def get_low_stock_items(db: Session):
    return db.query(models.Inventory).filter(models.Inventory.quantity < models.Inventory.threshold).all()
