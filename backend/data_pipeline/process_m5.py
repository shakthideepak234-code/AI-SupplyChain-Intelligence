
from pathlib import Path
import gc

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "datasets" / "raw" / "m5"
OUTPUT_DIR = PROJECT_ROOT / "datasets" / "processed"

SALES_FILE = RAW_DIR / "sales_train_validation.csv"
CALENDAR_FILE = RAW_DIR / "calendar.csv"
OUTPUT_FILE = OUTPUT_DIR / "weekly_demand.csv"

CHUNK_SIZE = 100

ID_COLUMNS = [
    "id", "item_id", "dept_id",
    "cat_id", "store_id", "state_id"
]


def process_m5():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading calendar...")

    calendar = pd.read_csv(CALENDAR_FILE)

    # Read sales column names
    sales_columns = pd.read_csv(
        SALES_FILE, nrows=0
    ).columns.tolist()

    day_columns = [
        col for col in sales_columns
        if col.startswith("d_")
    ]

    day_to_week = dict(
        zip(calendar["d"], calendar["wm_yr_wk"])
    )

    day_weeks = [
        day_to_week[day] for day in day_columns
    ]

    week_codes, week_ids = pd.factorize(
    np.array(day_weeks), sort=True

    )

    number_of_weeks = len(week_ids)

    # Start a fresh output file
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    first_chunk = True
    total_records = 0

    print("Processing with NumPy aggregation...")

    for chunk_number, chunk in enumerate(
        pd.read_csv(SALES_FILE, chunksize=CHUNK_SIZE),
        start=1
    ):
        sales_values = chunk[day_columns].to_numpy(
            dtype=np.int32
        )

        row_count = len(chunk)

        weekly_values = np.zeros(
            (row_count, number_of_weeks),
            dtype=np.int64
        )

        row_indices = np.arange(row_count)[:, None]

        np.add.at(
            weekly_values,
            (row_indices, week_codes[None, :]),
            sales_values
        )

        metadata = chunk[ID_COLUMNS].reset_index(drop=True)

        weekly_data = metadata.loc[
            metadata.index.repeat(number_of_weeks)
        ].reset_index(drop=True)

        weekly_data["week_id"] = np.tile(
            week_ids, row_count
        )

        weekly_data["units_sold"] = weekly_values.reshape(-1)

        weekly_data.to_csv(
            OUTPUT_FILE,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False
        )

        total_records += len(weekly_data)
        first_chunk = False

        print(
            f"Chunk {chunk_number} completed | "
            f"Total records: {total_records:,}"
        )

        del sales_values, weekly_values, weekly_data, chunk
        gc.collect()

    print("\nProcessing completed!")
    print(f"Total weekly records: {total_records:,}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_m5()
