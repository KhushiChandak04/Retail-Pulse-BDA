
# RetailPulse — E-Commerce Sales and Customer Behaviour Analytics

A Big Data Analytics mini-project built with **Python, Pandas, Apache Spark (PySpark), Spark SQL, CSV, and Power BI**.

## Project Title

**RetailPulse: E-Commerce Sales and Customer Behaviour Analytics Using Apache Spark and Power BI**

## Objective

Analyze real-world online retail transaction data to understand:

- Revenue and sales trends
- Product performance
- Country-wise sales
- Customer purchase frequency
- Customer spending behaviour
- Repeat versus one-time customers
- Cancellation activity

## Technology Stack

- Python
- Pandas
- Apache Spark / PySpark
- Spark SQL
- CSV
- Power BI
- Git / GitHub
- VS Code

## Dataset

The supplied dataset is **Online Retail II**, a real-world retail transaction dataset.

Local file:

```text
data/raw/online_retail_II.csv
```

The raw CSV is intentionally ignored by Git because of its size. See `docs/dataset_analysis.md` for the profile and cleaning decisions.

## Architecture

```text
             Online Retail II CSV
                      |
                      v
                Pandas Cleaning
                      |
                      v
                     CSV
                      |
                      v
                   PySpark
                      |
                      v
                Spark SQL Views
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
    Sales         Products       Customers
    Analysis      Analysis       Behaviour
       |              |              |
       +--------------+--------------+
                      |
                      v
             Analytical CSV Outputs
                      |
                      v
                  Power BI
                      |
                      v
          Interactive Dashboard
```

## Data-Handling Decisions

The uploaded file contains both sales and cancellation/return activity.

### Valid sales

A row is treated as a valid sale when:

```text
invoice is not a cancellation
AND quantity > 0
AND price > 0
```

### Customer behaviour

Customer-level analysis also requires a non-null `customer_id`.

This is important because the supplied dataset contains many valid sales with missing customer IDs. Those transactions are still included in overall sales analysis, but they cannot be attributed to a customer.

### Revenue

```text
Revenue = Quantity × Price
```

### Cancellations

An invoice beginning with `C` or a negative quantity is classified as cancellation activity.

Cancellations remain available for a separate cancellation analysis rather than being silently deleted.

## Dataset Profile from the Supplied File

- Rows: **1,067,371**
- Columns: **8**
- Date range: **2009-12-01 to 2011-12-09**
- Unique invoices: **53,628**
- Unique stock codes: **5,305**
- Identifiable customers: **5,942**
- Missing customer IDs: **243,007 rows**
- Missing descriptions: **4,382 rows**
- Exact duplicate rows: **34,335**
- Invoices beginning with `C`: **19,494**
- Negative-quantity rows: **22,950**
- Project-classified cancellation rows (C-prefix OR negative quantity): **22,951**
- Non-positive-price rows: **6,207**
- Countries: **43**

### Initial analytical profile

For valid sales with an identifiable customer:

- Valid rows: **805,549**
- Valid invoices: **36,969**
- Identifiable customers: **5,878**
- Repeat customers with more than one order: **4,255**
- One-time customers: **1,623**
- Revenue: **17,743,429.18**

For all valid sales, including anonymous customers:

- Valid rows: **1,041,670**
- Valid invoices: **40,077**
- Revenue: **20,972,594.57**

The distinction is intentional and is documented in `docs/dataset_analysis.md`.

## Setup

Use Python 3.10+ and Java 17+ with PySpark 4.2.x. The project installs the Spark SQL extras so the required SQL-side Python dependencies are included.

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Then run:

```powershell
python src/run_project.py
```

## Generated Outputs

```text
outputs/
├── data_quality_summary.csv
├── kpi_summary.csv
├── monthly_sales.csv
├── monthly_customer_activity.csv
├── product_sales.csv
├── top_products.csv
├── country_sales.csv
├── customer_analysis.csv
├── customer_segments.csv
├── cancellation_analysis.csv
└── sales_transactions.csv
```

## Power BI

Import the generated `outputs/sales_transactions.csv` into Power BI Desktop.

Then build:

- Revenue KPI
- Orders KPI
- Unique Customers KPI
- Average Order Value KPI
- Monthly Revenue Trend
- Top 10 Products
- Country Sales
- Customer Segments
- Customer Spending
- Cancellation Trend

See `powerbi/dashboard_guide.md`.

## GitHub Setup

```powershell
git init
git add .
git commit -m "Initial project setup"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

The raw dataset is ignored by `.gitignore`, so it will not be pushed to GitHub accidentally.

## Team Split

### Member 1
Pandas preprocessing and data-quality analysis.

### Member 2
PySpark and Spark SQL analytics.

### Member 3
Power BI dashboard, documentation, and presentation.

All members should understand the complete pipeline for the viva.
