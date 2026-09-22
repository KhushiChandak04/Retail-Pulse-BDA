
from pathlib import Path
import shutil
import sys

SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from config import RAW_DATA, PROCESSED_DIR, OUTPUT_DIR
from data_cleaning import clean_retail_data
from spark_pipeline import create_spark_session, load_transactions, register_views


QUERIES = {
    "data_quality_summary": """
        SELECT
            COUNT(*) AS cleaned_rows,
            COUNT(DISTINCT invoice) AS unique_invoices,
            COUNT(DISTINCT stock_code) AS unique_products,
            COUNT(DISTINCT customer_id) AS identifiable_customers,
            COUNT(DISTINCT country) AS countries,
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


def write_single_csv(result_df, target_path: Path):
    temp_path = OUTPUT_DIR / f"_tmp_{target_path.stem}"

    result_df.coalesce(1).write.mode("overwrite").option("header", True).csv(
        str(temp_path)
    )

    part_files = list(temp_path.glob("part-*.csv"))
    if not part_files:
        raise RuntimeError(f"Spark did not generate output for {target_path.name}")

    shutil.copy2(part_files[0], target_path)
    shutil.rmtree(temp_path, ignore_errors=True)


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
    clean_retail_data(RAW_DATA, processed_path)

    print("Step 2/4 - Starting Apache Spark...")
    spark = create_spark_session()

    try:
        print("Step 3/4 - Loading cleaned data into Spark...")
        df = load_transactions(spark, processed_path)
        register_views(df)

        print("Step 4/4 - Running Spark SQL analytics...")
        for name, sql_query in QUERIES.items():
            result = spark.sql(sql_query)
            write_single_csv(result, OUTPUT_DIR / f"{name}.csv")

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

        write_single_csv(
            fact_df,
            OUTPUT_DIR / "sales_transactions.csv"
        )

    finally:
        spark.stop()

    print("")
    print("RetailPulse pipeline completed successfully.")
    print(f"Processed data: {processed_path}")
    print(f"Outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
