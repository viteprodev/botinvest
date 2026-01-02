from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.api.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

from app.models.user import User

@router.post("/access-token")
def login_access_token(
    login_in: LoginRequest,
    db: Session = Depends(deps.get_db)
):
    # Find user by username
    user = db.query(User).filter(User.username == login_in.username).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not user.hashed_password:
        raise HTTPException(status_code=400, detail="Password not set for this user. Please set it via Telegram Bot first.")

    if not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    access_token = create_access_token(subject=user.telegram_id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "telegram_id": user.telegram_id,
            "full_name": user.full_name,
            "username": user.username,
            "photo_url": None, # or fetch if stored
            "balance": user.balance
        }
    }
