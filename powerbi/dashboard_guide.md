
# RetailPulse Power BI Dashboard Guide

## Main data table

After running:

```powershell
python src/run_project.py
```

import:

```text
outputs/sales_transactions.csv
```

Use **Home -> Get Data -> Text/CSV**.

Rename the table to:

```text
Sales
```

## Recommended DAX measures

```DAX
Total Revenue =
SUM(Sales[revenue])
```

```DAX
Total Orders =
DISTINCTCOUNT(Sales[invoice])
```

```DAX
Total Units =
SUM(Sales[quantity])
```

```DAX
Unique Customers =
DISTINCTCOUNT(Sales[customer_id])
```

```DAX
Average Order Value =
DIVIDE([Total Revenue], [Total Orders])
```

## Page 1 — Sales Overview

### KPI cards

- Total Revenue
- Total Orders
- Total Units
- Unique Customers
- Average Order Value

### Charts

**Monthly Revenue Trend**
- Line chart
- X-axis: invoice_date
- Y-axis: Total Revenue

**Top 10 Products**
- Bar chart
- Axis: description
- Value: Total Revenue
- Apply Top N = 10

Use `month` from `outputs/monthly_sales.csv` for the monthly trend when you
want the already aggregated Spark SQL result. Use `invoice_date` from `Sales`
when you want date slicers to affect the fact table directly.

**Revenue by Country**
- Bar chart or map
- Location: country
- Value: Total Revenue

## Page 2 — Customer Behaviour

Import:

```text
outputs/customer_analysis.csv
outputs/customer_segments.csv
```

Display:

- Customer segment
- Order frequency
- Total spend
- Average order value
- Recency
- Unique products

The customer segments are project-defined thresholds: one order is One-time,
2-5 orders is Repeat, and more than 5 orders is Frequent. They are not labels
provided by the source dataset.

## Page 3 — Cancellation Analysis

Import:

```text
outputs/cancellation_analysis.csv
```

Display:

- Cancellation invoices by month
- Cancelled units by month
- Cancellation value by month
- Cancellation trend

## Suggested slicers

- Invoice Date
- Country
- Product
- Customer ID

Cancellation rows are retained in the cleaned dataset, but they are excluded
from `Sales` and therefore do not inflate sales KPIs.

## Viva explanation

> VS Code is the development environment for the Python, Pandas, PySpark, and Spark SQL pipeline. Spark produces analytical CSV outputs, and Power BI consumes those outputs as the visualization layer.

## Design guidance

Keep the dashboard analytical. Use clear KPIs, trends, comparisons, and filters. Avoid excessive decorative elements.
