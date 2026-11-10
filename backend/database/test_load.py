
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_FILE = PROJECT_ROOT / "datasets" / "processed" / "weekly_demand.csv"

load_dotenv(PROJECT_ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

BATCH_SIZE = 2000
TEST_LIMIT = 1000


def test_load():
    print("Reading test records...")

    data = pd.read_csv(CSV_FILE, nrows=TEST_LIMIT)
    data = data[
    ["item_id", "store_id", "week_id", "units_sold"]
]

    print(f"Records selected: {len(data):,}")

    try:
        with engine.begin() as connection:
            data.to_sql(
                "weekly_demand",
                con=connection,
                if_exists="append",
                index=False,
                chunksize=500,
                method="multi"
            )

        print("Test upload successful!")

        with engine.connect() as connection:
            count = connection.execute(
                text("SELECT COUNT(*) FROM weekly_demand")
            ).scalar()

            size = connection.execute(
                text("""
                    SELECT pg_size_pretty(
                        pg_database_size(current_database())
                    )
                """)
            ).scalar()

        print(f"Database demand records: {count:,}")
        print(f"Current database size: {size}")

    except Exception as error:
        print("ERROR TYPE:", type(error).__name__)
        print("ORIGINAL ERROR:", repr(getattr(error, "orig", error)))
        import traceback
        traceback.print_exc()

    finally:
        engine.dispose()


if __name__ == "__main__":
    test_load()
