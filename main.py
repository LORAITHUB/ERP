from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
import crud
import database
from database import engine, Base, get_db
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    require_roles
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/register", response_model=schemas.UserResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=models.RoleEnum(payload.role.value)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/login", response_model=schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token_payload = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_payload)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile", response_model=schemas.UserResponse)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/manager-only")
def manager_only(current_user: models.User = Depends(require_roles([models.RoleEnum.manager]))):
    return {"message": f"Hello Manager {current_user.name}"}

@app.get("/")
def root():
    return {"status": "ok", "service": "auth"}



@app.get("/rooms", response_model=list[schemas.Room])
def get_rooms(db: Session = Depends(get_db)):
    return crud.get_rooms(db)

@app.post("/rooms", response_model=schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    return crud.create_room(db, room)


@app.put("/rooms/{room_id}/status")
def update_room_status(room_id: int, update: schemas.RoomStatusUpdate, db: Session = Depends(get_db)):
    room = crud.update_room_status(db, room_id, update.status)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": f"Room {room_id} status updated to {update.status}"}

# ---- Bookings ----
@app.post("/bookings", response_model=schemas.Booking)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    return crud.create_booking(db, booking)

@app.put("/bookings/{booking_id}/checkin", response_model=schemas.Booking)
def checkin_booking(booking_id: int, db: Session = Depends(get_db)):
    return crud.checkin_booking(db, booking_id)

@app.put("/bookings/{booking_id}/checkout", response_model=schemas.Booking)
def checkout_booking(booking_id: int, db: Session = Depends(get_db)):
    return crud.checkout_booking(db, booking_id)

# ---- Housekeeping ----
@app.post("/housekeeping", response_model=schemas.Housekeeping)
def create_housekeeping(hk: schemas.HousekeepingCreate, db: Session = Depends(get_db)):
    return crud.create_housekeeping(db, hk)

@app.put("/housekeeping/{hk_id}", response_model=schemas.Housekeeping)
def update_housekeeping(hk_id: int, status: str, db: Session = Depends(get_db)):
    return crud.update_housekeeping(db, hk_id, status)

@app.get("/tables", response_model=list[schemas.TableResponse])
def list_tables(db: Session = Depends(get_db)):
    return db.query(models.Table).all()


@app.post('/create_tables', response_model=schemas.TableResponse)
def create_table(req: schemas.TableResponse, db: Session = Depends(get_db)):
    existing_table = db.query(models.Table).filter(models.Table.table_number == req.table_number).first()
    if existing_table:
        raise HTTPException(status_code=400, detail="Table number already exists")

    
    table = models.Table(
        table_number=req.table_number,
        capacity=req.capacity,
        status=req.status
    )
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@app.post("/reservations", response_model=schemas.ReservationResponse)
def create_reservation(req: schemas.CreateReservation, db: Session = Depends(get_db)):
    table = db.query(models.Table).filter(models.Table.id == req.table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    reservation = models.Reservation(
        user_id=req.user_id,
        table_id=req.table_id,
        reservation_time=req.reservation_time
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation

@app.get("/menu", response_model=list[schemas.MenuItemResponse])
def list_menu(db: Session = Depends(get_db)):
    return db.query(models.MenuItem).all()

@app.post("/menu", response_model=schemas.MenuItemResponse)
def add_menu_item(req: schemas.CreateMenuItem, db: Session = Depends(get_db)):
    item = models.MenuItem(**req.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.post("/orders", response_model=schemas.OrderResponse)
def create_order(req: schemas.CreateOrder, db: Session = Depends(get_db)):
    order = models.Order(
        table_id=req.table_id,
        staff_id=req.staff_id,
        total_price=0
    )
    db.add(order)
    db.flush()  

    total_price = 0
    for item in req.items:
        order_item = models.OrderItem(
            order_id=order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price=item.price
        )
        total_price += item.price * item.quantity
        db.add(order_item)

    order.total_price = total_price
    db.commit()
    db.refresh(order)
    return order


@app.put("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, req: schemas.UpdateOrderStatus, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = req.status
    db.commit()
    db.refresh(order)
    return order


@app.post("/billing", response_model=schemas.BillingOut)
def create_billing(bill: schemas.BillingCreate, db: Session = Depends(get_db)):
    db_bill = models.Billing(**bill.dict())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

@app.get("/billing/{id}", response_model=schemas.BillingOut)
def get_billing(id: int, db: Session = Depends(get_db)):
    bill = db.query(models.Billing).filter(models.Billing.id == id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Billing not found")
    return bill
 

@app.get("/inventory", response_model=list[schemas.InventoryOut])
def list_inventory(db: Session = Depends(database.get_db)):
    return crud.get_inventory_items(db)

@app.post("/inventory", response_model=schemas.InventoryOut)
def add_inventory(item: schemas.InventoryItemCreate, db: Session = Depends(database.get_db)):
    return crud.create_inventory_item(db, item)

@app.put("/{item_id}", response_model=schemas.InventoryOut)
def update_inventory(
    item_id: int, 
    update: schemas.InventoryItemUpdate, 
    db: Session = Depends(database.get_db)
):
    updated_item = crud.update_inventory_quantity(db, item_id, update.quantity)
    
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with id {item_id} not found."
        )
    return updated_item

@app.get("/inventory/low-stock")
def low_stock_items(db: Session = Depends(get_db)):
    items = crud.get_low_stock_items(db)
    return items

@app.get("/reports/occupancy")
def get_occupancy_report(session: Session = Depends(get_db)):
    try:
        total_rooms = session.query(Room).count()
        occupied_rooms = session.query(Room).filter(Room.status == 'occupied').count()
        occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms else 0
        return {
            "total_rooms": total_rooms,
            "occupied_rooms": occupied_rooms,
            "occupancy_rate": round(occupancy_rate, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate occupancy report")

@app.get("/reports/revenue")
def get_revenue_report(session: Session = Depends(get_db), start_date=None, end_date=None):
    try:
        if start_date and end_date:
            period_billings = session.query(Billing).filter(Billing.created_at.between(start_date, end_date))
        total_revenue = sum([amount for (total_amount,) in period_billings.all()])
        return {"total_revenue": round(total_revenue, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate revenue report")

@app.get("/reports/staff-performance")
def get_staff_performance(session: Session = Depends(get_db)):
    try:
        staff_ids = session.query(User.id).filter(User.role == 'staff').all()
        performance = {}
        for (staff_id,) in staff_ids:
            completed_hk = session.query(Housekeeping).filter(
                Housekeeping.staff_id == staff_id,
                Housekeeping.status == 'completed'
            ).count()
            orders_served = session.query(Order).filter(
                Order.staff_id == staff_id,
                Order.status.in_(['served', 'billed'])
            ).count()
            performance[staff_id] = {
                "housekeeping_completed": completed_hk,
                "orders_served": orders_served
            }
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate staff performance report")

@app.post("/notifications/low-stock")
def trigger_low_stock_alert(session: Session = Depends(get_db)):
    try:
        low_stock_items = session.query(Inventory).filter(Inventory.quantity <= Inventory.threshold).all()
        alerts = [
            {"item_name": item.item_name, "req_quantity": (item.threshold - item.quantity)}
            for item in low_stock_items
        ]
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to trigger low stock alert")

@app.post("/notifications/over_booking")
def trigger_overbooking_alert(session: Session = Depends(get_db)):
    try:
        alerts = []
        bookings = session.query(Booking).filter(
            Booking.status == 'booked'
        ).order_by(Booking.room_id, Booking.check_in).all()

        grouped = defaultdict(list)
        for booking in bookings:
            grouped[booking.room_id].append(booking)

        for room_id, room_bookings in grouped.items():
            for i in range(1, len(room_bookings)):
                prev = room_bookings[i - 1]
                curr = room_bookings[i]
                if curr.check_in < prev.check_out:
                    alerts.append({
                        'room_id': prev.room_id,
                        'clash_booking_id': [prev.id, curr.id]
                    })
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to check for overbooking")
