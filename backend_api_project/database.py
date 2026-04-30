import psycopg2
from backend_api_project.config import Config

def get_db_connection():
    conn = psycopg2.connect(Config.DATABASE_URL)
    return conn