from database import get_db_connection

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            reset_token TEXT,
            profile_image TEXT
        )
    """)

    conn.commit()
    conn.close()