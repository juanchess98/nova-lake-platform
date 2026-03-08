"""Transform bronze payments into validated silver payments."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table
from transformations.bronze_to_silver.common import dedupe_latest

VALID_STATUSES = ["paid", "pending", "failed"]
VALID_PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer", "wallet"]


def standardize_payments(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("payment_id", F.upper(F.trim(F.col("payment_id"))))
        .withColumn("order_id", F.upper(F.trim(F.col("order_id"))))
        .withColumn("payment_timestamp", F.to_timestamp("payment_timestamp"))
        .withColumn("payment_method", F.lower(F.trim(F.col("payment_method"))))
        .withColumn("payment_status", F.lower(F.trim(F.col("payment_status"))))
        .withColumn("payment_amount", F.round(F.col("payment_amount").cast("decimal(12,2)"), 2))
        .withColumn("currency", F.upper(F.trim(F.col("currency"))))
    )


def apply_quality_checks(df: DataFrame) -> DataFrame:
    valid_df = (
        df.filter(F.col("payment_id").rlike(r"^PAY\d{8}$"))
        .filter(F.col("order_id").rlike(r"^ORD\d{8}$"))
        .filter(F.col("payment_timestamp").isNotNull())
        .filter(F.col("payment_method").isin(VALID_PAYMENT_METHODS))
        .filter(F.col("payment_status").isin(VALID_STATUSES))
        .filter(F.col("payment_amount") >= 0)
        .filter(F.col("currency") == F.lit("USD"))
    )
    return dedupe_latest(valid_df, ["payment_id"])


def enforce_order_referential_integrity(payments_df: DataFrame, orders_df: DataFrame) -> DataFrame:
    return payments_df.join(
        orders_df.select("order_id", "order_timestamp", "total_amount"),
        on="order_id",
        how="inner",
    ).filter(F.col("payment_timestamp") >= F.col("order_timestamp"))


def main() -> None:
    logger = get_logger("novalake.jobs.transform.payments_silver")
    spark = create_spark_session("novalake_payments_bronze_to_silver")
    logger.info("Starting transform job: bronze.payments -> silver.payments")

    try:
        bronze_df = spark.table(table_identifier("bronze", "payments"))
        silver_orders_df = spark.table(table_identifier("silver", "orders"))

        standardized_df = standardize_payments(bronze_df)
        quality_df = apply_quality_checks(standardized_df)
        joined_df = enforce_order_referential_integrity(quality_df, silver_orders_df)

        silver_df = joined_df.select(
            "payment_id",
            "order_id",
            "payment_timestamp",
            "payment_method",
            "payment_status",
            "payment_amount",
            "currency",
            "_ingestion_timestamp",
            "_source_file",
        )

        ensure_namespace(spark, "silver")
        write_iceberg_table(silver_df, "silver", "payments")
        logger.info("Completed transform job: wrote table novalake.silver.payments")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
