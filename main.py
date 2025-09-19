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
