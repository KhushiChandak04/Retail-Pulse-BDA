
-- RetailPulse reference Spark SQL queries.
-- The executable pipeline is src/run_project.py.

-- Total revenue
SELECT ROUND(SUM(revenue), 2) AS total_revenue
FROM sales_transactions;

-- Monthly revenue
SELECT
    date_format(invoice_date, 'yyyy-MM') AS month,
    ROUND(SUM(revenue), 2) AS revenue
FROM sales_transactions
GROUP BY date_format(invoice_date, 'yyyy-MM')
ORDER BY month;

-- Top products
SELECT
    stock_code,
    first(description) AS description,
    ROUND(SUM(revenue), 2) AS revenue,
    SUM(quantity) AS units_sold
FROM sales_transactions
GROUP BY stock_code
ORDER BY revenue DESC
LIMIT 10;

-- Country sales
SELECT
    country,
    ROUND(SUM(revenue), 2) AS revenue,
    COUNT(DISTINCT invoice) AS orders
FROM sales_transactions
GROUP BY country
ORDER BY revenue DESC;

-- Customer behaviour
SELECT
    customer_id,
    COUNT(DISTINCT invoice) AS order_frequency,
    ROUND(SUM(revenue), 2) AS total_spent,
    COUNT(DISTINCT stock_code) AS unique_products
FROM customer_sales_transactions
GROUP BY customer_id
ORDER BY total_spent DESC;
