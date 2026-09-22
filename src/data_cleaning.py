
from pathlib import Path

import pandas as pd

from config import REQUIRED_COLUMNS


COLUMN_MAP = {
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
}


def clean_retail_data(input_path: Path, output_path: Path) -> pd.DataFrame:
    """
    Clean the supplied Online Retail II CSV.

    The cleaned file intentionally keeps:
    - cancellation/return rows for separate analysis
    - rows with missing customer IDs for overall sales analysis
    """

    df = pd.read_csv(input_path, low_memory=False)
    df = df.rename(columns=COLUMN_MAP)

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    for col in ["invoice", "stock_code", "description", "country"]:
        df[col] = df[col].astype("string").str.strip()

    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")
    df["customer_id"] = df["customer_id"].astype("Int64").astype("string")

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")

    df["description"] = df["description"].fillna("Unknown Product")

    df = df.dropna(
        subset=["invoice", "stock_code", "invoice_date", "quantity", "price"]
    )

    df["is_cancellation"] = (
        df["invoice"].str.upper().str.startswith("C", na=False)
        | (df["quantity"] < 0)
    )

    df["revenue"] = df["quantity"] * df["price"]

    df["is_valid_sale"] = (
        (~df["is_cancellation"])
        & (df["quantity"] > 0)
        & (df["price"] > 0)
    )

    df["is_duplicate"] = df.duplicated(keep=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return df
