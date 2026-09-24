# RetailPulse Project Status

## Completed

- Pandas cleaning for the supplied Online Retail II CSV.
- Spark local session, typed CSV loading, temporary views, and Spark SQL analytics.
- Overall sales analysis retains valid rows without customer IDs.
- Customer analysis uses only valid sales with known customer IDs.
- Cancellation and return activity remains available for separate analysis.
- CSV outputs prepared for Power BI.
- Independent Pandas-versus-Spark validation written to `outputs/validation_summary.csv`.
- Windows setup avoids requiring a separate Hadoop/HDFS installation.
- The processed dataset is prepared for Git LFS sharing at
  `data/processed/cleaned_retail_transactions.csv`.

## Completed Automatically by This Agent

- Rebuilt and verified the single `.venv` environment with Python 3.12.
- Installed dependencies from `requirements.txt`.
- Removed the duplicate `.venv-1` environment.
- Ran the test suite and Python compilation checks.
- Ran `src/run_project.py` successfully against the complete local dataset.
- Verified all expected output CSV files and their key headers.
- Verified validation status is PASS for all compared metrics.
- Verified Git LFS 3.5.1 is installed and the processed file is 114.35 MB.
- Committed and pushed the processed dataset through Git LFS to `origin/main`.

## Remaining

- Build and format the dashboard in Power BI Desktop.
- Add screenshots and interpretation to the academic report.
- Complete final GitHub review and confirm only intended files are tracked.
- Rehearse the project demonstration and viva answers.

## Runtime Environment Requirements

- Python 3.10 or newer; Python 3.12 is recommended.
- Java 17 or newer for PySpark; Java 22 was used for the local verification.
- Dependencies installed with `python -m pip install -r requirements.txt`.
- Spark runs in local mode. Hadoop/HDFS, Hive, Kafka, databases, and web
  frameworks are not required by this project.
- Power BI Desktop is required only for the interactive dashboard stage.

## Final Verification Checklist

- [x] Environment verified
- [x] Dependencies installed
- [x] Tests pass
- [x] Dataset schema matches code
- [x] Pandas cleaning runs
- [x] PySpark starts successfully
- [x] Spark SQL queries run successfully
- [x] All expected output CSVs are generated
- [x] Output schema is correct
- [x] Key results are independently validated
- [x] Power BI input file is ready
- [x] Documentation is updated
- [x] Processed dataset committed and pushed through Git LFS
- [ ] Git status is clean after reviewing generated files
- [ ] Power BI dashboard is built manually
- [ ] Report, presentation, demo, and viva preparation are complete
