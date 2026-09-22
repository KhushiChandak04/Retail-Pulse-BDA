
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data_cleaning import clean_retail_data


def test_clean_retail_data(tmp_path):
    raw = tmp_path / "raw.csv"
    processed = tmp_path / "processed.csv"

    sample = pd.DataFrame({
        "Invoice": ["10001", "C10002", "10003"],
        "StockCode": ["A", "B", "C"],
        "Description": ["Item A", None, "Item C"],
        "Quantity": [2, -1, 3],
        "InvoiceDate": [
            "2009-12-01 08:00:00",
            "2009-12-01 09:00:00",
            "2009-12-02 10:00:00",
        ],
        "Price": [10.0, 5.0, 2.0],
        "Customer ID": [12345, 12345, None],
        "Country": ["United Kingdom", "United Kingdom", "France"],
    })
    sample.to_csv(raw, index=False)

    result = clean_retail_data(raw, processed)

    assert processed.exists()
    assert list(result.columns[:8]) == [
        "invoice", "stock_code", "description", "quantity",
        "invoice_date", "price", "customer_id", "country"
    ]
    assert result.loc[0, "revenue"] == 20.0
    assert bool(result.loc[1, "is_cancellation"])
    assert result.loc[1, "description"] == "Unknown Product"
