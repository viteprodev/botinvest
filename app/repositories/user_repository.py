from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_telegram_id(self, telegram_id: int) -> User:
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def create(self, telegram_id: int, username: str = None, full_name: str = None) -> User:
        user = User(telegram_id=telegram_id, username=username, full_name=full_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_balance(self, user_id: int, amount: float) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.balance += amount
            self.db.commit()
            self.db.refresh(user)
        return user
