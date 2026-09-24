# Spark SQL Validation

All analytical queries were executed through the existing
`src/run_project.py` pipeline against the supplied Online Retail II dataset.
Each output was checked against independent Pandas aggregations over the same
cleaned data. No analytical query definitions were changed.

| Analysis | Query/View | Expected Logic | Validation Result | PASS/FAIL | Notes |
|---|---|---|---|---|---|
| `kpi_summary.csv` | `kpi_summary` / `sales_transactions` | Revenue, distinct orders, units, known customers, and average order value over valid sales. | Columns, numeric types, nulls, counts, revenue, and AOV match. | PASS | Revenue: `20,972,594.57`; orders: `40,077`; customers: `5,878`. |
| `monthly_sales.csv` | `monthly_sales` / `sales_transactions` | Group valid sales by `yyyy-MM`, with revenue, units, and distinct orders. | 25 months, chronological ordering, totals, and monthly groups match. | PASS | SQL rounds revenue to two decimals; independent comparisons use the same rounding. |
| `monthly_customer_activity.csv` | `monthly_customer_activity` / `customer_sales_transactions` | Group valid sales with non-null customer IDs by month. | Monthly customer counts, orders, revenue, columns, and ordering match. | PASS | Customer view correctly excludes anonymous transactions. |
| `product_sales.csv` | `product_sales` / `sales_transactions` | Group valid sales by `stock_code`, ordered by descending revenue. | 4,916 product groups, revenue totals, units, orders, and descending sort match. | PASS | SQL rounds revenue; identifier formatting from CSV reload was canonicalized for comparison. |
| `top_products.csv` | `top_products` / `sales_transactions` | Return the 10 stock codes with the highest valid-sales revenue. | Exactly 10 rows; top-N membership, revenue, and descending order match. | PASS | No query change required. |
| `country_sales.csv` | `country_sales` / `sales_transactions` | Group valid sales by country with revenue, units, orders, and distinct customers. | 43 countries, counts, revenue total, customer counts, and descending sort match. | PASS | Numeric CSV inference and two-decimal SQL rounding were normalized for comparison. |
| `customer_analysis.csv` | `customer_analysis` / `customer_sales_transactions` | Calculate order frequency, units, products, spend, AOV, last purchase, recency, and country per known customer. | 5,878 customers, non-null output fields, descending spend, IDs, counts, and spend totals match. | PASS | Monetary values are intentionally rounded to two decimals by SQL; customer IDs were compared canonically. |
| `customer_segments.csv` | `customer_segments` / `customer_sales_transactions` | Assign one-time, repeat, or frequent segments from distinct order counts. | Three segments; customer counts sum to 5,878 and segment membership/counts match. | PASS | Average spend and frequency are intentionally rounded to two decimals. |
| `cancellation_analysis.csv` | `cancellation_analysis` / `retail_transactions` | Group cancellation rows by month using distinct invoices and absolute units/value. | Monthly groups, invoice counts, absolute units, values, columns, and ordering match. | PASS | Uses the existing rule: invoice starts with `C` OR quantity is negative. |
| `sales_transactions.csv` | Fact query / `sales_transactions` | Export every valid sale with the required Power BI fields. | 1,041,670 rows; columns, dates, numeric fields, invoice count, revenue, and row-level revenue calculation match. | PASS | Null `customer_id` is expected for anonymous valid sales and is intentionally retained. |

## Cross-Checks

- Spark SQL valid-sales revenue: `20,972,594.57`.
- Pandas valid-sales revenue: `20,972,594.57`.
- Spark valid-sales rows: `1,041,670`.
- Spark valid invoices: `40,077`.
- Spark known customers: `5,878`.
- Spark cancellation rows: `22,951`.
- No unintended nulls were found in analytical dimensions or measures.
- Revenue totals reconcile after applying the SQL queries' documented
  two-decimal rounding.

## Output Regeneration

The full pipeline was rerun successfully with exit code `0`. The following
ten requested CSV outputs were regenerated, along with
`validation_summary.csv`:

```text
kpi_summary.csv
monthly_sales.csv
monthly_customer_activity.csv
product_sales.csv
top_products.csv
country_sales.csv
customer_analysis.csv
customer_segments.csv
cancellation_analysis.csv
sales_transactions.csv
```

No query was incorrect, so no analytical definition was changed.