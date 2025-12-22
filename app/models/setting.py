from sqlalchemy import Column, String
from app.models.base import Base

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)

    def __repr__(self):
        return f"<Setting(key={self.key}, value={self.value})>"
