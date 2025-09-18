from fastapi import FastAPI, Depends, HTTPException, status
from database import Base, engine
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserOut, TokenOut, LoginRequest
from auth import get_password_hash,verify_password,create_access_token,get_current_user,require_role

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospitality ERP")


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_in.role not in ("manager", "staff", "guest"):
        raise HTTPException(status_code=400, detail="Invalid role")

    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/login", response_model=TokenOut)
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_req.email).first()
    if not user or not verify_password(login_req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/admin-only")
def admin_only(current_user: User = Depends(require_role(["manager"]))):
    return {"message": f"Hello {current_user.name}, you are a manager!"}
    
@app.get("/")
def demo():
    return {'msg' : 'Hii'}
