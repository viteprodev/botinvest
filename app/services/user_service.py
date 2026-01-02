from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.models.user import User

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, telegram_id: int, username: str, full_name: str) -> User:
        user = self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            user = self.user_repo.create(telegram_id, username, full_name)
        return user

    def get_balance(self, telegram_id: int) -> float:
        user = self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return 0.0
        return user.balance
        
    def claim_bonus(self, telegram_id: int) -> bool:
        user = self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")
        
        if user.bonus_claimed:
            raise ValueError("Bonus sudah pernah diklaim.")
            
        # Check for at least one APPROVED topup
        from app.models.transaction import Transaction, TransactionType, TransactionStatus
        has_tx = self.db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.TOPUP,
            Transaction.amount > 0,
            Transaction.status == TransactionStatus.APPROVED
        ).first()
        
        if not has_tx:
            raise ValueError("Anda harus melakukan minimal 1x transaksi Topup untuk klaim bonus.")
            
        # Award Bonus
        user.bonus_claimed = True
        user.balance += 500000 # Add Rp 500.000
        self.db.commit()
        return True
