# Repository Audit

This repository was checked against the supplied `data/raw/online_retail_II.csv`.

## Verified

- The raw CSV has the expected eight source columns.
- Pandas cleaning maps the source headers to the project schema.
- Missing customer IDs remain nullable and anonymous valid sales are retained.
- Cancellation rows remain available for separate analysis.
- The complete Spark SQL pipeline ran successfully in local mode.
- All analytical CSV outputs and `validation_summary.csv` were generated.
- Independent Pandas-versus-Spark validation passed for row counts, orders,
  customers, revenue, units, and every monthly revenue value.

## Runtime decision

RetailPulse does not use Hadoop/HDFS as a selected project technology. PySpark
contains Hadoop filesystem libraries internally, but the pipeline runs with a
local Spark session and writes final CSV files through Python. This avoids the
Windows-only `winutils.exe` requirement while keeping Spark SQL as the core
analytics engine.
