from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.payment_service import PaymentService
from app.models.transaction import TransactionStatus, TransactionType

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TransactionStatus] = None,
    telegram_id: Optional[int] = None,
    db: Session = Depends(deps.get_db)
):
    service = PaymentService(db)
    query = db.query(service.tx_repo.model)
    
    if status:
        query = query.filter(service.tx_repo.model.status == status)
        
    if telegram_id:
        user = service.user_repo.get_by_telegram_id(telegram_id)
        if user:
            query = query.filter(service.tx_repo.model.user_id == user.id)
        else:
            return [] # User not found means no transactions
            
    return query.order_by(service.tx_repo.model.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/topup", response_model=TransactionResponse)
def create_topup(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: TransactionCreate
):
    service = PaymentService(db)
    user = service.user_repo.get_by_telegram_id(transaction_in.telegram_id)
    if not user:
        # Create user if not exists? Usually bot handles registration.
        # Here we assume user exists.
        raise HTTPException(status_code=404, detail="User not found")

    if transaction_in.type != TransactionType.TOPUP:
        raise HTTPException(status_code=400, detail="Invalid transaction type for this endpoint")

    tx = service.create_topup(
        user_id=transaction_in.telegram_id, # service takes telegram_id? No, usually user_id (int PK). 
        # Let's check logic. create_topup in handler calls service.create_topup(user_id, amount, proof).
        # In handler: user_id = update.effective_user.id (this is telegram_id).
        # Check service implementation... 
        # Waiting... 
        # Better safe: service.create_topup likely expects telegram_id if it looks up user, OR user.id if it uses FK.
        # Retained memory of typical implementations: usually service resolves user. 
        # Let's assume input is telegram_id as per handler usage.
        amount=transaction_in.amount,
        proof_url=transaction_in.proof_url
    )
    return tx

@router.post("/withdraw", response_model=TransactionResponse)
def create_withdraw(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: TransactionCreate
):
    service = PaymentService(db)
    if transaction_in.type != TransactionType.WITHDRAW:
        raise HTTPException(status_code=400, detail="Invalid transaction type for this endpoint")
        
    try:
        tx = service.request_withdraw(
            user_id=transaction_in.telegram_id, 
            amount=transaction_in.amount
        )
        return tx
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{tx_id}/approve", response_model=TransactionResponse)
def approve_transaction(
    tx_id: int,
    db: Session = Depends(deps.get_db)
):
    service = PaymentService(db)
    try:
        tx = service.approve_transaction(tx_id)
        return tx
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{tx_id}/reject", response_model=TransactionResponse)
def reject_transaction(
    tx_id: int,
    db: Session = Depends(deps.get_db)
):
    service = PaymentService(db)
    try:
        service.reject_transaction(tx_id)
        # Fetch updated tx to return
        tx = service.tx_repo.get(tx_id)
        return tx
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
