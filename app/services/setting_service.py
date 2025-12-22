from sqlalchemy.orm import Session
from app.models.setting import Setting

class SettingService:
    def __init__(self, db: Session):
        self.db = db

    def get_setting(self, key: str, default: str = "") -> str:
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        if setting:
            return setting.value
        return default

    def set_setting(self, key: str, value: str):
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            self.db.add(setting)
        self.db.commit()
        self.db.refresh(setting)
        return setting
