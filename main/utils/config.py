from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / ".env"

# Try to load .env file
if env_path.exists():
    load_dotenv(env_path, override=True)

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root@localhost:3306/office_games")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    ALLOW_NEW_REGISTRATIONS: bool = os.getenv("ALLOW_NEW_REGISTRATIONS", "true").lower() == "true"

settings = Settings()
