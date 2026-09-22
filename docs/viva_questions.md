
# Viva Questions

## Why did you use Apache Spark?
The dataset contains more than one million transaction rows, making it a suitable demonstration of distributed big-data processing.

## Why use Pandas as well?
Pandas is convenient for initial inspection, type conversion, data cleaning, and creating a clean input for Spark.

## What is Spark SQL?
Spark SQL is the structured query engine used to execute SQL analytics over Spark data.

## How is revenue calculated?
Revenue is calculated as Quantity multiplied by Price.

## Why are rows with missing Customer ID not deleted?
They may still represent valid sales. They are retained for overall sales analysis and excluded only from customer-level metrics.

## How are cancellations identified?
Invoices beginning with C and negative quantity rows are classified as cancellation activity.

## How are repeat customers identified?
Customers are grouped by distinct invoice count. More than one order means the customer is a repeat purchaser.

## How do VS Code and Power BI work together?
VS Code runs Python, Pandas, PySpark, and Spark SQL. The pipeline generates CSV outputs, which Power BI imports for visualization.
