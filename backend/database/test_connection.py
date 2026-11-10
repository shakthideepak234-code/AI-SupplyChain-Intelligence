
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), version()")
        )
        database_name, version = result.fetchone()

        print("Database connection successful!")
        print("Database:", database_name)
        print("PostgreSQL:", version.split(",")[0])

except Exception as error:
    print("Database connection failed!")
    print(type(error).__name__, error)

finally:
    engine.dispose()
