from sqlalchemy.orm import Session
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.models.transaction import Transaction, TransactionType, TransactionStatus

class PaymentService:
    def __init__(self, db: Session):
        self.tx_repo = TransactionRepository(db)
        self.user_repo = UserRepository(db)



    def create_topup(self, telegram_id: int, amount: float, proof_url: str):
        user = self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")
        return self.tx_repo.create(user.id, TransactionType.TOPUP, amount, proof_url)

    def request_withdraw(self, telegram_id: int, amount: float):
        user = self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")
        if user.balance < amount:
            raise ValueError("Saldo tidak mencukupi")
        return self.tx_repo.create(user.id, TransactionType.WITHDRAW, amount)

    def count_approved_topups(self, user_id: int) -> int:
        return self.tx_repo.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.TOPUP,
            Transaction.status == TransactionStatus.APPROVED
        ).count()


    def approve_transaction(self, tx_id: int):
        tx = self.tx_repo.get_by_id(tx_id)
        if not tx:
            raise ValueError("Transaction not found")
        if tx.status != TransactionStatus.PENDING:
            raise ValueError("Transaction ID already processed")
            
        # Update Status
        self.tx_repo.update_status(tx_id, TransactionStatus.APPROVED)
        
        # Update Balance based on type
        if tx.type == TransactionType.TOPUP:
            self.user_repo.update_balance(tx.user_id, tx.amount)
        elif tx.type == TransactionType.WITHDRAW:
            self.user_repo.update_balance(tx.user_id, -tx.amount)
            
        return tx

    def reject_transaction(self, tx_id: int):
        tx = self.tx_repo.get_by_id(tx_id)
        if not tx:
            raise ValueError("Transaction not found")
        if tx.status != TransactionStatus.PENDING:
            raise ValueError("Transaction ID already processed")
            
        return self.tx_repo.update_status(tx_id, TransactionStatus.REJECTED)

    def get_pending_transactions(self):
        return self.tx_repo.get_pending()
