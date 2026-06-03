import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development-only-secret")
ALGORITHM = "HS256"
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
password_hash = PasswordHash.recommended()

class Auth(BaseModel):
    id: int
    username: str
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequired(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_token(user_id:int)-> str:
    expires= datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {
        "sub": str(user_id),
        "exp": expires,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=Auth)
def register(data: RegisterRequest, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.username == data.username))
    if user is not None:
        raise HTTPException(status_code=409, detail="User already exists")
    hashed_password = password_hash.hash(data.password)
    user = User(username=data.username, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return { "id": user.id, "username": user.username }

@router.post("/login", response_model=Token)
def login(data: LoginRequired, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.username == data.username))
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    password_corr= password_hash.verify(data.password, user.password_hash)
    if not password_corr:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer" }

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],db: Annotated[Session, Depends(get_db)],) -> User:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
