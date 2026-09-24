
import csv
import math
from pathlib import Path
import sys

import pandas as pd

SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from config import RAW_DATA, PROCESSED_DIR, OUTPUT_DIR
from data_cleaning import clean_retail_data
from spark_pipeline import create_spark_session, load_transactions, register_views


QUERIES = {
    "data_quality_summary": """
        SELECT
            COUNT(*) AS total_rows,
            COUNT(*) AS cleaned_rows,
            COUNT(DISTINCT invoice) AS unique_invoices,
            COUNT(DISTINCT stock_code) AS unique_products,
            COUNT(DISTINCT customer_id) AS identifiable_customers,
            COUNT(DISTINCT country) AS countries,
            SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END)
                AS missing_customer_rows,
            SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END)
                AS rows_without_customer_id,
            SUM(CASE WHEN is_cancellation THEN 1 ELSE 0 END)
                AS cancellation_rows,
            SUM(CASE WHEN is_duplicate THEN 1 ELSE 0 END)
                AS flagged_duplicate_rows
        FROM retail_transactions
    """,

    "kpi_summary": """
        SELECT
            ROUND(SUM(revenue), 2) AS total_revenue,
            COUNT(DISTINCT invoice) AS total_orders,
            SUM(quantity) AS total_units_sold,
            COUNT(DISTINCT customer_id) AS unique_customers,
            ROUND(
                SUM(revenue) / COUNT(DISTINCT invoice),
                2
            ) AS average_order_value
        FROM sales_transactions
    """,

    "monthly_sales": """
        SELECT
            date_format(invoice_date, 'yyyy-MM') AS month,
            ROUND(SUM(revenue), 2) AS revenue,
            SUM(quantity) AS units_sold,
            COUNT(DISTINCT invoice) AS orders
        FROM sales_transactions
        GROUP BY date_format(invoice_date, 'yyyy-MM')
        ORDER BY month
    """,

    "monthly_customer_activity": """
        SELECT
            date_format(invoice_date, 'yyyy-MM') AS month,
            COUNT(DISTINCT customer_id) AS active_customers,
            COUNT(DISTINCT invoice) AS orders,
            ROUND(SUM(revenue), 2) AS revenue
        FROM customer_sales_transactions
        GROUP BY date_format(invoice_date, 'yyyy-MM')
        ORDER BY month
    """,

    "product_sales": """
        SELECT
            stock_code,
            first(description) AS description,
            ROUND(SUM(revenue), 2) AS revenue,
            SUM(quantity) AS units_sold,
            COUNT(DISTINCT invoice) AS orders
        FROM sales_transactions
        GROUP BY stock_code
        ORDER BY revenue DESC
    """,

    "top_products": """
        SELECT
            stock_code,
            first(description) AS description,
            ROUND(SUM(revenue), 2) AS revenue,
            SUM(quantity) AS units_sold,
            COUNT(DISTINCT invoice) AS orders
        FROM sales_transactions
        GROUP BY stock_code
        ORDER BY revenue DESC
        LIMIT 10
    """,

    "country_sales": """
        SELECT
            country,
            ROUND(SUM(revenue), 2) AS revenue,
            SUM(quantity) AS units_sold,
            COUNT(DISTINCT invoice) AS orders,
            COUNT(DISTINCT customer_id) AS customers
        FROM sales_transactions
        GROUP BY country
        ORDER BY revenue DESC
    """,

    "customer_analysis": """
        WITH customer_stats AS (
            SELECT
                customer_id,
                COUNT(DISTINCT invoice) AS order_frequency,
                SUM(quantity) AS units_purchased,
                COUNT(DISTINCT stock_code) AS unique_products,
                ROUND(SUM(revenue), 2) AS total_spent,
                ROUND(
                    SUM(revenue) / COUNT(DISTINCT invoice),
                    2
                ) AS average_order_value,
                MAX(invoice_date) AS last_purchase_date,
                first(country, true) AS country
            FROM customer_sales_transactions
            GROUP BY customer_id
        ),
        max_date AS (
            SELECT MAX(invoice_date) AS max_purchase_date
            FROM customer_sales_transactions
        )
        SELECT
            c.customer_id,
            c.order_frequency,
            c.units_purchased,
            c.unique_products,
            c.total_spent,
            c.average_order_value,
            c.last_purchase_date,
            DATEDIFF(m.max_purchase_date, c.last_purchase_date) AS recency_days,
            c.country
        FROM customer_stats c
        CROSS JOIN max_date m
        ORDER BY c.total_spent DESC
    """,

    "customer_segments": """
        SELECT
            CASE
                WHEN order_frequency = 1 THEN 'One-time Customer'
                WHEN order_frequency BETWEEN 2 AND 5 THEN 'Repeat Customer'
                ELSE 'Frequent Customer'
            END AS customer_segment,
            COUNT(*) AS customers,
            ROUND(AVG(total_spent), 2) AS average_customer_spend,
            ROUND(AVG(order_frequency), 2) AS average_order_frequency
        FROM (
            SELECT
                customer_id,
                COUNT(DISTINCT invoice) AS order_frequency,
                SUM(revenue) AS total_spent
            FROM customer_sales_transactions
            GROUP BY customer_id
        ) customer_stats
        GROUP BY
            CASE
                WHEN order_frequency = 1 THEN 'One-time Customer'
                WHEN order_frequency BETWEEN 2 AND 5 THEN 'Repeat Customer'
                ELSE 'Frequent Customer'
            END
        ORDER BY customers DESC
    """,

    "cancellation_analysis": """
        SELECT
            date_format(invoice_date, 'yyyy-MM') AS month,
            COUNT(DISTINCT invoice) AS cancellation_invoices,
            SUM(ABS(quantity)) AS cancelled_units,
            ROUND(SUM(ABS(revenue)), 2) AS cancellation_value
        FROM retail_transactions
        WHERE is_cancellation = true
        GROUP BY date_format(invoice_date, 'yyyy-MM')
        ORDER BY month
    """,
}


def _csv_value(value):
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat(sep=" ")
    return value


def write_single_csv(result_df, target_path: Path):
    """Write Spark results without requiring a Windows Hadoop installation."""
    with target_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(result_df.columns)
        for row in result_df.toLocalIterator():
            writer.writerow(_csv_value(value) for value in row)


def _reference_metrics(cleaned_df: pd.DataFrame):
    sales_df = cleaned_df[cleaned_df["is_valid_sale"]].copy()
    metrics = {
        "total_rows": len(cleaned_df),
        "total_orders": sales_df["invoice"].nunique(),
        "unique_customers": sales_df["customer_id"].dropna().nunique(),
        "total_revenue": round(float(sales_df["revenue"].sum()), 2),
        "total_units_sold": float(sales_df["quantity"].sum()),
        "monthly_sales_rows": sales_df["invoice_date"].dt.strftime("%Y-%m").nunique(),
        "monthly_sales_revenue": round(float(sales_df["revenue"].sum()), 2),
    }
    monthly_revenue = sales_df.groupby(
        sales_df["invoice_date"].dt.strftime("%Y-%m")
    )["revenue"].sum()
    metrics.update({
        f"monthly_revenue_{month}": round(float(revenue), 2)
        for month, revenue in monthly_revenue.items()
    })
    return metrics


def _spark_metric_rows(results):
    kpi = results["kpi_summary"][0].asDict()
    quality = results["data_quality_summary"][0].asDict()
    monthly = results["monthly_sales"]
    metrics = {
        "total_rows": quality["total_rows"],
        "total_orders": kpi["total_orders"],
        "unique_customers": kpi["unique_customers"],
        "total_revenue": float(kpi["total_revenue"]),
        "total_units_sold": float(kpi["total_units_sold"]),
        "monthly_sales_rows": len(monthly),
        "monthly_sales_revenue": round(sum(float(row["revenue"]) for row in monthly), 2),
    }
    metrics.update({
        f"monthly_revenue_{row['month']}": float(row["revenue"])
        for row in monthly
    })
    return metrics


def write_validation_summary(cleaned_df, results):
    reference = _reference_metrics(cleaned_df)
    spark_values = _spark_metric_rows(results)
    rows = []
    for metric, pandas_value in reference.items():
        spark_value = spark_values[metric]
        difference = float(spark_value) - float(pandas_value)
        passed = math.isclose(float(spark_value), float(pandas_value), abs_tol=0.01)
        rows.append({
            "metric": metric,
            "pandas_value": pandas_value,
            "spark_value": spark_value,
            "difference": round(difference, 2),
            "status": "PASS" if passed else "FAIL",
        })

    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "validation_summary.csv", index=False)
    failed = [row["metric"] for row in rows if row["status"] != "PASS"]
    if failed:
        raise RuntimeError(f"Independent validation failed for: {failed}")


def main():
    if not RAW_DATA.exists():
        raise FileNotFoundError(
            f"Dataset not found at {RAW_DATA}. "
            "Place online_retail_II.csv in data/raw/."
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    processed_path = PROCESSED_DIR / "cleaned_retail_transactions.csv"

    print("Step 1/4 - Cleaning data with Pandas...")
    cleaned_df = clean_retail_data(RAW_DATA, processed_path)

    print("Step 2/4 - Starting Apache Spark...")
    spark = create_spark_session()

    try:
        print("Step 3/4 - Loading cleaned data into Spark...")
        df = load_transactions(spark, processed_path)
        register_views(df)

        print("Step 4/4 - Running Spark SQL analytics...")
        results = {}
        for name, sql_query in QUERIES.items():
            result = spark.sql(sql_query)
            results[name] = result.collect()
            write_single_csv(result, OUTPUT_DIR / f"{name}.csv")

        write_validation_summary(cleaned_df, results)

        # Detailed fact table for Power BI.
        fact_df = spark.sql("""
            SELECT
                invoice,
                stock_code,
                description,
                quantity,
                invoice_date,
                price,
                customer_id,
                country,
                revenue
            FROM sales_transactions
        """)

        write_single_csv(fact_df, OUTPUT_DIR / "sales_transactions.csv")

    finally:
        spark.stop()

    print("")
    print("RetailPulse pipeline completed successfully.")
    print(f"Processed data: {processed_path}")
    print(f"Outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
