"""Transform bronze orders into validated silver orders."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table
from transformations.bronze_to_silver.common import dedupe_latest

VALID_STATUSES = ["completed", "pending", "cancelled"]
VALID_PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer", "wallet"]


def standardize_orders(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("order_id", F.upper(F.trim(F.col("order_id"))))
        .withColumn("customer_id", F.upper(F.trim(F.col("customer_id"))))
        .withColumn("order_timestamp", F.to_timestamp("order_timestamp"))
        .withColumn("order_status", F.lower(F.trim(F.col("order_status"))))
        .withColumn("currency", F.upper(F.trim(F.col("currency"))))
        .withColumn("subtotal_amount", F.round(F.col("subtotal_amount").cast("decimal(12,2)"), 2))
        .withColumn("tax_amount", F.round(F.col("tax_amount").cast("decimal(12,2)"), 2))
        .withColumn("shipping_amount", F.round(F.col("shipping_amount").cast("decimal(12,2)"), 2))
        .withColumn("total_amount", F.round(F.col("total_amount").cast("decimal(12,2)"), 2))
        .withColumn("payment_method", F.lower(F.trim(F.col("payment_method"))))
    )


def apply_quality_checks(df: DataFrame) -> DataFrame:
    valid_df = (
        df.filter(F.col("order_id").rlike(r"^ORD\d{8}$"))
        .filter(F.col("customer_id").rlike(r"^CUST\d{6}$"))
        .filter(F.col("order_timestamp").isNotNull())
        .filter(F.col("order_status").isin(VALID_STATUSES))
        .filter(F.col("currency") == F.lit("USD"))
        .filter(F.col("subtotal_amount") >= 0)
        .filter(F.col("tax_amount") >= 0)
        .filter(F.col("shipping_amount") >= 0)
        .filter(F.col("payment_method").isin(VALID_PAYMENT_METHODS))
        .filter(F.round(F.col("subtotal_amount") + F.col("tax_amount") + F.col("shipping_amount"), 2) == F.col("total_amount"))
    )
    return dedupe_latest(valid_df, ["order_id"])


def enforce_customer_referential_integrity(orders_df: DataFrame, customers_df: DataFrame) -> DataFrame:
    return orders_df.join(customers_df.select("customer_id"), on="customer_id", how="inner")


def main() -> None:
    logger = get_logger("novalake.jobs.transform.orders_silver")
    spark = create_spark_session("novalake_orders_bronze_to_silver")
    logger.info("Starting transform job: bronze.orders -> silver.orders")

    try:
        bronze_orders_df = spark.table(table_identifier("bronze", "orders"))
        silver_customers_df = spark.table(table_identifier("silver", "customers"))

        standardized_df = standardize_orders(bronze_orders_df)
        quality_df = apply_quality_checks(standardized_df)
        silver_df = enforce_customer_referential_integrity(quality_df, silver_customers_df)

        ensure_namespace(spark, "silver")
        write_iceberg_table(silver_df, "silver", "orders")
        logger.info("Completed transform job: wrote table novalake.silver.orders")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
