from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionType, TransactionStatus

class TransactionBase(BaseModel):
    amount: float
    type: TransactionType

class TransactionCreate(TransactionBase):
    telegram_id: int # Input by Telegram ID, backend will resolve to user_id
    proof_url: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    status: TransactionStatus
    proof_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
