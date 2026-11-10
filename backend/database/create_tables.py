
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine

from models import Base

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

try:
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")

    print("Tables:")
    for table_name in Base.metadata.tables:
        print(f"- {table_name}")

finally:
    engine.dispose()
