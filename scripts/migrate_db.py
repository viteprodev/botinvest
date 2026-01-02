
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path so we can import app modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate():
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not set.")
        return

    # Fix for SQLAlchemy using psycopg 3 (same logic as app/config.py)
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    print(f"Connecting to database...")
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            # DEBUG: Check active connections
            print("Checking active connections...")
            result = connection.execute(text("SELECT pid, application_name, client_addr, state, query FROM pg_stat_activity WHERE state != 'idle';"))
            rows = result.fetchall()
            print(f"Active/Idle-in-transaction connections: {len(rows)}")
            for row in rows:
                print(f" - PID: {row[0]}, App: {row[1]}, IP: {row[2]}, State: {row[3]}, Query: {row[4]}")
            
            # Check for blocking locks specifically
            print("Checking for blocking locks...")
            lock_query = text("""
                SELECT pid, mode, granted 
                FROM pg_locks 
                WHERE relation = 'users'::regclass AND pid != pg_backend_pid();
            """)
            
            blocking_pids = []
            try:
                lock_rows = connection.execute(lock_query).fetchall()
                if lock_rows:
                    print(f"!! FOUND BLOCKING LOCKS on 'users' table: {lock_rows}")
                    for row in lock_rows:
                        blocking_pids.append(row[0])
                else:
                    print("No explicit locks found on 'users' table.")
            except Exception as e:
                print(f"Could not check locks (table might not exist yet?): {e}")

            if blocking_pids:
                print(f"The following PIDs are holding locks: {blocking_pids}")
                confirm = input("Do you want to FORCE KILL these connections to allow migration? (y/n): ")
                if confirm.lower() == 'y':
                    for pid in blocking_pids:
                        print(f"Killing PID {pid}...")
                        try:
                            connection.execute(text(f"SELECT pg_terminate_backend({pid});"))
                        except Exception as kille:
                            print(f"Failed to kill {pid}: {kille}")
                    print("Blockers killed. Proceeding...")
                else:
                    print("Migration aborted by user.")
                    return

            print("Checking if 'hashed_password' column exists...")
            
            # Check if column exists
            result = connection.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='hashed_password';"
            ))
            
            if result.fetchone():
                print("Column 'hashed_password' already exists. Skipping.")
            else:
                print("Adding 'hashed_password' column...")
                print("WARNING: This requires an ACCESS EXCLUSIVE lock. If this hangs, stop all other DB connections.")
                
                # Disable timeouts to wait as long as needed OR fail fast?
                # Let's try disabling statement timeout to prevent "QueryCanceled"
                connection.execute(text("SET statement_timeout = 0;"))
                connection.execute(text("SET lock_timeout = 0;"))
                
                connection.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR;"))
                connection.commit()
                print("Migration successful: Added 'hashed_password' column.")
                
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
