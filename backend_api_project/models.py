from backend_api_project.database import get_db_connection

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            password TEXT,
            verification_token TEXT,
            is_verified INTEGER DEFAULT 0,
            reset_token TEXT,
            profile_image TEXT,
            role TEXT DEFAULT 'user'      
        )
    """)

    conn.commit()
    conn.close()