# Repository Audit

This starter repository was checked against the supplied `online_retail_II.csv`.

## Checks completed

- ZIP integrity test passed.
- Python syntax compilation passed for all 5 Python files.
- Dataset header names were inspected directly.
- The rename mapping in `src/data_cleaning.py` matches the uploaded headers:
  `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`,
  `Customer ID`, `Country`.
- The cleaning function was executed against the complete supplied CSV.
- The calculated row/invoice/customer/revenue counts were checked.
- Spark SQL expressions were reviewed against the current Spark SQL/PySpark
  4.2 API documentation.

## Runtime limitation

The execution environment used for this audit does not have PySpark installed,
and outbound package installation is unavailable. Therefore the Spark JVM
pipeline itself could not be executed here.

The project has been aligned to the current PySpark 4.2 installation guidance:
Python 3.10+, Java 17+, and the Spark SQL extras.

The first runtime test must therefore be performed on the development machine
after `pip install -r requirements.txt`.
