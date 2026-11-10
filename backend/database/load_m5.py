
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert

from models import Product, Store

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = PROJECT_ROOT / "datasets" / "raw" / "m5" / "sales_train_validation.csv"

load_dotenv(PROJECT_ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

CHUNK_SIZE = 10_000

def load_master_data():
    total_products = 0
    total_stores = 0

    print("Loading product and store master data...")

    try:
        with engine.begin() as connection:
            for chunk in pd.read_csv(
                RAW_FILE,
                usecols=["item_id", "dept_id", "cat_id", "store_id", "state_id"],
                chunksize=CHUNK_SIZE
            ):
                products = (
                    chunk[["item_id", "dept_id", "cat_id"]]
                    .drop_duplicates()
                    .to_dict("records")
                )

                stores = (
                    chunk[["store_id", "state_id"]]
                    .drop_duplicates()
                    .to_dict("records")
                )

                if products:
                    statement = insert(Product).values(products)
                    statement = statement.on_conflict_do_nothing(
                        index_elements=["item_id"]
                    )
                    result = connection.execute(statement)
                    total_products += result.rowcount

                if stores:
                    statement = insert(Store).values(stores)
                    statement = statement.on_conflict_do_nothing(
                        index_elements=["store_id"]
                    )
                    result = connection.execute(statement)
                    total_stores += result.rowcount

        print("\nMaster data loading completed!")
        print(f"Products inserted: {total_products}")
        print(f"Stores inserted: {total_stores}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    load_master_data()
