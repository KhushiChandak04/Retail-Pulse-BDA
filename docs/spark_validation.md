# Spark Data-Loading Validation

Validation was run against the supplied `data/raw/online_retail_II.csv` and
the existing `src/data_cleaning.py` and `src/spark_pipeline.py` logic. No
pipeline logic was changed.

## Checks

| Check | Expected value | Actual value | Status | Explanation |
|---|---:|---:|---|---|
| Spark row count matches cleaned input | 1,067,371 | 1,067,371 | PASS | Spark loaded every row from the cleaned CSV. |
| Expected columns exist | 12 columns | Same 12 columns | PASS | Names and order match the Pandas-cleaned output. |
| `invoice_date` parsing | Timestamp | `timestamp` | PASS | Spark converts the cleaned date strings with `to_timestamp`. |
| `quantity` type | Numeric | `double` | PASS | Spark casts `quantity` to `double`. |
| `price` type | Numeric | `double` | PASS | Spark casts `price` to `double`. |
| Missing customer IDs | 243,007 | 243,007 | PASS | Missing IDs remain null in Spark. |
| Customer sales view has no missing IDs | 0 | 0 | PASS | `customer_sales_transactions` filters null customer IDs. |
| Cancellation rows | 22,951 | 22,951 | PASS | Matches `invoice starts with C OR quantity < 0`. |
| Cancellation-rule mismatches | 0 | 0 | PASS | Stored `is_cancellation` agrees with the documented predicate. |
| Valid sales rows | 1,041,670 | 1,041,670 | PASS | Matches non-cancellation rows with positive quantity and price. |
| Valid-sale-rule mismatches | 0 | 0 | PASS | Stored `is_valid_sale` agrees with the project logic. |
| Valid-sales revenue | 20,972,594.57 | 20,972,594.57 | PASS | Pandas and Spark agree for the sales KPI population. |
| Cleaned revenue including cancellations | 19,287,250.57 | 19,287,250.57 | PASS | Both stages agree before filtering cancellation activity. |
| Revenue calculation mismatches | 0 rows | 0 rows | PASS | Every Spark row satisfies `revenue = quantity * price`. |

## Columns Verified

```text
invoice, stock_code, description, quantity, invoice_date, price,
customer_id, country, is_cancellation, revenue, is_valid_sale, is_duplicate
```

## Interpretation

The Spark loading and transformation stage is consistent with the Pandas
cleaning stage. Cancellation rows remain in `retail_transactions` for separate
analysis, while `sales_transactions` contains only valid sales. Customer
analytics use `customer_sales_transactions`, which excludes rows with missing
customer IDs.

The cleaned-revenue total is lower than valid-sales revenue because cancellation
rows have negative revenue and remain in the full cleaned dataset. This is
expected and is not a Pandas-versus-Spark discrepancy.

## Commands Used

```powershell
$env:JAVA_HOME = (Resolve-Path .\.tools\jdk-17).Path
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
\.venv\Scripts\python.exe -m pytest -q
```

The existing test suite passed: `1 passed`.