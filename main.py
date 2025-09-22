from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
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
        query = session.query(Billing.total_amount).filter(Billing.payment_status == 'paid')
        if start_date and end_date:
            query = query.filter(Billing.created_at.between(start_date, end_date))
        total_revenue = sum([amount for (amount,) in query.all()])
        return {"total_revenue": round(total_revenue, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate revenue report")

@app.get("/reports/staff-performance")
def get_staff_performance(session: Session = Depends(get_db)):
    try:
        staff_ids = session.query(User.id).filter(User.role == 'staff').all()
        performance = {}
        for (staff_id,) in staff_ids:
            completed_tasks = session.query(Housekeeping).filter(
                Housekeeping.staff_id == staff_id,
                Housekeeping.status == 'completed'
            ).count()
            orders_served = session.query(Order).filter(
                Order.staff_id == staff_id,
                Order.status.in_(['served', 'billed'])
            ).count()
            performance[staff_id] = {
                "housekeeping_completed": completed_tasks,
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

