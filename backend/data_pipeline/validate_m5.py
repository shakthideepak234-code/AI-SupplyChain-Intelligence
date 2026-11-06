
from pathlib import Path
import pandas as pd

# Locate project dataset folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "datasets" / "raw" / "m5"

FILES = [
    "calendar.csv",
    "sales_train_validation.csv",
    "sales_train_evaluation.csv",
    "sell_prices.csv",
    "sample_submission.csv",
]

print("=" * 60)
print("M5 DATASET VALIDATION REPORT")
print("=" * 60)

for filename in FILES:
    file_path = DATA_DIR / filename

    print(f"\nChecking: {filename}")
    print("-" * 50)

    if not file_path.exists():
        print("ERROR: File not found!")
        continue

    total_rows = 0
    missing_values = None
    columns = None

    try:
        # Read large files in smaller chunks
        for chunk in pd.read_csv(file_path, chunksize=5000):
            total_rows += len(chunk)

            if missing_values is None:
                columns = chunk.columns.tolist()
                missing_values = pd.Series(
                    0, index=columns, dtype="int64"
                )

            missing_values += chunk.isnull().sum()

        print(f"Total records : {total_rows:,}")
        print(f"Total columns : {len(columns)}")
        print(f"File size     : {file_path.stat().st_size / (1024**2):.2f} MB")

        missing_total = int(missing_values.sum())
        print(f"Missing values: {missing_total:,}")

        if missing_total:
            print("Columns with missing values:")
            print(missing_values[missing_values > 0])
        else:
            print("No missing values found.")

    except Exception as error:
        print(f"Validation error: {error}")

print("\n" + "=" * 60)
print("VALIDATION COMPLETED")
print("=" * 60)
