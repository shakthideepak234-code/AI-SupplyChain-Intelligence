from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def train_forecast(item_id, store_id):

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

        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    if len(df) < 10:
        return {"error": "Insufficient historical data"}

    df["week_id"] = pd.to_numeric(df["week_id"])
    df["units_sold"] = pd.to_numeric(df["units_sold"])

    df["lag_1"] = df["units_sold"].shift(1)
    df["lag_2"] = df["units_sold"].shift(2)
    df["lag_3"] = df["units_sold"].shift(3)
    df["rolling_mean"] = df["units_sold"].shift(1).rolling(4).mean()

    df = df.dropna()

    features = ["week_id", "lag_1", "lag_2", "lag_3", "rolling_mean"]

    X = df[features]
    y = df["units_sold"]

    split = int(len(df) * 0.8)

    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = RandomForestRegressor(
        n_estimators=50,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)

    print(f"Model MAE: {mae:.2f}")

    history = df["units_sold"].tolist()
    next_week = int(df["week_id"].iloc[-1]) + 1

    forecasts = []

    for week in range(1, 5):

        lag_1 = history[-1]
        lag_2 = history[-2]
        lag_3 = history[-3]
        rolling_mean = sum(history[-4:]) / 4

        prediction_input = pd.DataFrame(
            [[next_week, lag_1, lag_2, lag_3, rolling_mean]],
            columns=features
        )

        prediction = max(
            0,
            float(model.predict(prediction_input)[0])
        )

        forecasts.append({
            "week_ahead": week,
            "forecast_units": round(prediction, 2)
        })

        history.append(prediction)
        next_week += 1

    return forecasts


if __name__ == "__main__":

    result = train_forecast(
        item_id="FOODS_2_019",
        store_id="CA_1"
    )

    print("\nML Demand Forecast:")

    if isinstance(result, list):
        for row in result:
            print(row)
    else:
        print(result)

    engine.dispose()