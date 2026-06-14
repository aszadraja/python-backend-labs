from database import get_db_connection

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        age INTEGER NOT NULL CHECK (age > 0),
        password TEXT NOT NULL,
        verification_token TEXT,
        is_verified BOOLEAN DEFAULT FALSE,
        reset_token TEXT,
        profile_image TEXT,
        role TEXT CHECK (role IN ('user', 'admin')) DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()