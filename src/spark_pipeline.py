
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def create_spark_session():
    return (
        SparkSession.builder
        .appName("RetailPulseECommerceAnalytics")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def load_transactions(spark, path: Path):
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(path))
    )

    return (
        df.withColumn("invoice_date", F.to_timestamp("invoice_date"))
          .withColumn("quantity", F.col("quantity").cast("double"))
          .withColumn("price", F.col("price").cast("double"))
          .withColumn("revenue", F.col("revenue").cast("double"))
          .withColumn("customer_id", F.col("customer_id").cast("string"))
          .withColumn("is_cancellation", F.col("is_cancellation").cast("boolean"))
          .withColumn("is_valid_sale", F.col("is_valid_sale").cast("boolean"))
          .withColumn("is_duplicate", F.col("is_duplicate").cast("boolean"))
    )


def register_views(df):
    df.createOrReplaceTempView("retail_transactions")

    sales_df = df.filter(
        (F.col("is_valid_sale") == True)
        & (F.col("quantity") > 0)
        & (F.col("price") > 0)
    )
    sales_df.createOrReplaceTempView("sales_transactions")

    customer_sales_df = sales_df.filter(F.col("customer_id").isNotNull())
    customer_sales_df.createOrReplaceTempView("customer_sales_transactions")
