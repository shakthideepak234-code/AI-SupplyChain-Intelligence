from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert

from models import WeeklyDemand

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_FILE = PROJECT_ROOT / "datasets" / "processed" / "weekly_demand.csv"

load_dotenv(PROJECT_ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

CHUNK_SIZE = 1000


def load_weekly_demand():
    total_loaded = 0

    print("Loading weekly demand data...")

    try:
        for chunk in pd.read_csv(CSV_FILE, chunksize=CHUNK_SIZE):
            if total_loaded >= 500_000:
               break

            remaining = 500_000 - total_loaded
            chunk = chunk.head(remaining)

            chunk = chunk[
                ["item_id", "store_id", "week_id", "units_sold"]
            ]

            records = chunk.to_dict("records")

            with engine.begin() as connection:
                statement = insert(WeeklyDemand).values(records)

                statement = statement.on_conflict_do_nothing(
                    index_elements=["item_id", "store_id", "week_id"]
                )

                connection.execute(statement)

            total_loaded += len(records)
            print(f"Processed: {total_loaded:,} records")

        print("\nWeekly demand loading completed!")

    finally:
        engine.dispose()


if __name__ == "__main__":
    load_weekly_demand()