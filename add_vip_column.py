from app.database import engine
from sqlalchemy import text

def add_vip_column():
    with engine.connect() as conn:
        try:
            # Check if column exists (PostgreSQL specific check, but simplified "ALTER TABLE ... ADD COLUMN IF NOT EXISTS" works in PG 9.6+)
            # Using raw SQL is safest for this quick fix without Alembic
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_vip BOOLEAN DEFAULT FALSE;"))
            conn.commit()
            print("Migration successful: Added is_vip column.")
        except Exception as e:
            print(f"Migration failed or column already exists: {e}")

if __name__ == "__main__":
    add_vip_column()
