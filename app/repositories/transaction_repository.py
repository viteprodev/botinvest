from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from typing import List

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, tx_type: TransactionType, amount: float, proof_url: str = None) -> Transaction:
        tx = Transaction(
            user_id=user_id,
            type=tx_type,
            amount=amount,
            proof_url=proof_url,
            status=TransactionStatus.PENDING
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def get_by_id(self, tx_id: int) -> Transaction:
        return self.db.query(Transaction).filter(Transaction.id == tx_id).first()

    def update_status(self, tx_id: int, status: TransactionStatus) -> Transaction:
        tx = self.get_by_id(tx_id)
        if tx:
            tx.status = status
            self.db.commit()
            self.db.refresh(tx)
        return tx

    def get_history(self, user_id: int, limit: int = 10) -> List[Transaction]:
        return self.db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.created_at.desc()).limit(limit).all()

    def get_pending(self) -> List[Transaction]:
        return self.db.query(Transaction).filter(Transaction.status == TransactionStatus.PENDING).all()
