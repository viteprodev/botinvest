import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_IDS = [int(id_str) for id_str in os.getenv("ADMIN_IDS", "").split(",") if id_str.strip()]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables.")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

# Fix for SQLAlchemy using psycopg 3
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
