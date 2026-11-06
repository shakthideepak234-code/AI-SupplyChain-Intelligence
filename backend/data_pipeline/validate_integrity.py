
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datasets" / "raw" / "m5"

print("=" * 60)
print("M5 DATA INTEGRITY REPORT")
print("=" * 60)

# 1. Check sales metadata
sales_file = DATA / "sales_train_validation.csv"

sales = pd.read_csv(
    sales_file,
    usecols=["id", "item_id", "store_id", "state_id",
             "cat_id", "dept_id"]
)

print("\n1. SALES METADATA")
print("Total products:", sales["item_id"].nunique())
print("Total stores:", sales["store_id"].nunique())
print("Unique product-store combinations:",
      sales[["item_id", "store_id"]].drop_duplicates().shape[0])
print("Duplicate product-store combinations:",
      sales.duplicated(["item_id", "store_id"]).sum())

# 2. Check negative sales
print("\n2. SALES QUANTITY CHECK")

negative_sales = 0
zero_sales = 0
sales_rows = 0

for chunk in pd.read_csv(
    sales_file,
    chunksize=1000
):
    daily_data = chunk.iloc[:, 6:]

    negative_sales += int((daily_data < 0).sum().sum())
    zero_sales += int((daily_data == 0).sum().sum())
    sales_rows += len(chunk)

print("Sales rows checked:", sales_rows)
print("Negative sales values:", negative_sales)
print("Zero sales values:", zero_sales)

# 3. Check selling prices
print("\n3. SELLING PRICE CHECK")

price_file = DATA / "sell_prices.csv"

invalid_prices = 0
missing_prices = 0
price_rows = 0
duplicate_price_hashes = []

for chunk in pd.read_csv(price_file, chunksize=200000):
    invalid_prices += int((chunk["sell_price"] <= 0).sum())
    missing_prices += int(chunk.isnull().sum().sum())
    price_rows += len(chunk)

    hashes = pd.util.hash_pandas_object(
        chunk[["store_id", "item_id", "wm_yr_wk"]],
        index=False
    ).to_numpy(dtype=np.uint64)

    duplicate_price_hashes.append(hashes)

all_hashes = np.concatenate(duplicate_price_hashes)
all_hashes.sort()

duplicate_prices = int(
    np.sum(all_hashes[1:] == all_hashes[:-1])
)

print("Price records checked:", f"{price_rows:,}")
print("Invalid prices:", invalid_prices)
print("Missing price values:", missing_prices)
print("Duplicate price keys (hash-based):", duplicate_prices)

# 4. Check calendar dates
print("\n4. CALENDAR CHECK")

calendar = pd.read_csv(DATA / "calendar.csv")

print("Calendar records:", len(calendar))
print("Duplicate d identifiers:",
      calendar["d"].duplicated().sum())
print("Duplicate calendar dates:",
      calendar["date"].duplicated().sum())

# 5. Product-store consistency
print("\n5. PRODUCT AND STORE CONSISTENCY")

price_metadata = pd.read_csv(
    price_file,
    usecols=["item_id", "store_id"]
)

sales_pairs = set(
    zip(sales["item_id"], sales["store_id"])
)

price_pairs = set(
    zip(price_metadata["item_id"], price_metadata["store_id"])
)

print("Price combinations not in sales:",
      len(price_pairs - sales_pairs))

print("\n" + "=" * 60)
print("INTEGRITY CHECK COMPLETED")
print("=" * 60)
