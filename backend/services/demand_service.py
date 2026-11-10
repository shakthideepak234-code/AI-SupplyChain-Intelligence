from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def get_total_demand():
    query = text("""
        SELECT COALESCE(SUM(units_sold), 0)
        FROM weekly_demand
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar()


def get_top_products(limit=10):
    query = text("""
        SELECT
            item_id,
            SUM(units_sold) AS total_units_sold
        FROM weekly_demand
        GROUP BY item_id
        ORDER BY total_units_sold DESC
        LIMIT :limit
    """)

    with engine.connect() as connection:
        result = connection.execute(query, {"limit": limit})
        return [dict(row._mapping) for row in result]


def get_store_demand():
    query = text("""
        SELECT
            store_id,
            SUM(units_sold) AS total_units_sold
        FROM weekly_demand
        GROUP BY store_id
        ORDER BY total_units_sold DESC
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        return [dict(row._mapping) for row in result]


if __name__ == "__main__":
    print("Total Demand:", get_total_demand())
    print("\nTop 10 Products:")
    for product in get_top_products():
        print(product)

    print("\nStore-wise Demand:")
    for store in get_store_demand():
        print(store)

    engine.dispose()