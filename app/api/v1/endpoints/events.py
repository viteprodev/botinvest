from fastapi import APIRouter, Depends, HTTPException, Header
from app.api import deps
from app.api import security
from app.services.user_service import UserService
from typing import Optional

router = APIRouter()

# Simple dependency to get current user from token
def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Token")
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Token Scheme")
        
    user_id = security.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid Token")
    return user_id

@router.post("/claim_bonus")
def claim_bonus(
    db = Depends(deps.get_db),
    telegram_id: int = Depends(get_current_user_id)
):
    service = UserService(db)
    try:
        service.claim_bonus(telegram_id)
        return {"status": "success", "message": "Bonus Rp 500.000 berhasil diklaim!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
