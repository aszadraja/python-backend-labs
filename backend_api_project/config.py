import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(BASE_DIR, ".env")

print("Loading .env from:", env_path)

load_dotenv(env_path)

print("SECRET_KEY =", os.getenv("SECRET_KEY"))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE", 15))
    REFRESH_TOKEN_EXPIRE = int(os.getenv("REFRESH_TOKEN_EXPIRE", 7))
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:kali@localhost:5432/mydb"
    )