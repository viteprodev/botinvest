from datetime import datetime, timedelta
from typing import Optional, Any, Union
import jwt
from app.config import TOKEN as BOT_TOKEN # Using BOT_TOKEN as secret for now

# Configuration
SECRET_KEY = BOT_TOKEN  # Ideally this should be a separate SECRET, but for Telegram Auth validation it's related. 
# Actually for JWT we should use a distinct SECRET. But for simplicity let's use a string derived from it or just a hardcoded one for this MVP.
JWT_SECRET = "your-super-secret-key-change-this" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except jwt.PyJWTError:
        return None

import hashlib
import os

def get_password_hash(password: str) -> str:
    salt = os.urandom(32).hex()
    pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or '$' not in hashed_password:
        return False
    salt, pwd_hash = hashed_password.split('$')
    return pwd_hash == hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
