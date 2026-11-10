from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def forecast_demand(item_id, store_id, weeks=4):

    query = text("""
        SELECT week_id, units_sold
        FROM weekly_demand
        WHERE item_id = :item_id
          AND store_id = :store_id
        ORDER BY week_id
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"item_id": item_id, "store_id": store_id}
        )

        data = pd.DataFrame(result.fetchall(), columns=result.keys())

    if len(data) < 4:
        return {"error": "Insufficient historical data"}

    data["units_sold"] = pd.to_numeric(data["units_sold"])

    average_demand = data["units_sold"].tail(4).mean()

    forecast = []

    for week in range(1, weeks + 1):
        forecast.append({
            "week_ahead": week,
            "forecast_units": round(float(average_demand), 2)
        })

    return forecast


if __name__ == "__main__":
    result = forecast_demand(
        item_id="FOODS_2_019",
        store_id="CA_1"
    )

    print("4-Week Demand Forecast:")
    for row in result:
        print(row)

    engine.dispose()