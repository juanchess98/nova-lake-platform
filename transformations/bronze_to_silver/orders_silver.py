"""Transform bronze orders into standardized silver orders."""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from core.spark import (
    create_spark_session,
    ensure_namespace,
    get_logger,
    table_identifier,
    write_iceberg_table,
)

VALID_STATUSES = ["pending", "paid", "shipped", "completed", "cancelled", "refunded"]
DEFAULT_PAYMENT_METHOD = "unknown"


def standardize_orders(bronze_orders_df: DataFrame) -> DataFrame:
    """Apply type casting and naming conventions to Bronze orders."""
    return (
        bronze_orders_df.withColumn("order_id", F.col("order_id").cast("long"))
        .withColumn("customer_id", F.col("customer_id").cast("long"))
        .withColumn("order_timestamp", F.to_timestamp("order_timestamp"))
        .withColumn("order_status", F.lower(F.trim(F.col("status"))))
        .withColumn("currency", F.upper(F.trim(F.col("currency"))))
        .withColumn("total_amount", F.round(F.col("total_amount").cast("decimal(12,2)"), 2))
        .withColumn("payment_method", F.lower(F.trim(F.col("payment_method"))))
        .drop("status")
    )


def apply_quality_checks(orders_df: DataFrame) -> DataFrame:
    """Apply lightweight quality filters and deterministic deduplication."""
    filtered_df = (
        orders_df.filter(F.col("order_id").isNotNull())
        .filter(F.col("customer_id").isNotNull())
        .filter(F.col("order_timestamp").isNotNull())
        .filter(F.col("total_amount").isNotNull())
        .filter(F.col("total_amount") >= 0)
        .filter(F.col("order_status").isin(VALID_STATUSES))
        .filter(F.length(F.col("currency")) == 3)
        .fillna({"payment_method": DEFAULT_PAYMENT_METHOD})
    )

    dedupe_window = Window.partitionBy("order_id").orderBy(
        F.col("_ingestion_timestamp").desc_nulls_last(),
        F.col("_source_file").desc_nulls_last(),
    )
    return (
        filtered_df.withColumn("_row_num", F.row_number().over(dedupe_window))
        .filter(F.col("_row_num") == 1)
        .drop("_row_num")
    )


def main() -> None:
    logger = get_logger("novalake.jobs.transform.orders_silver")
    spark = create_spark_session("novalake_orders_bronze_to_silver")
    logger.info("Starting transform job: bronze.orders -> silver.orders")

    try:
        bronze_orders_df = spark.table(table_identifier("bronze", "orders"))
        standardized_orders_df = standardize_orders(bronze_orders_df)
        silver_orders_df = apply_quality_checks(standardized_orders_df)

        ensure_namespace(spark, "silver")
        write_iceberg_table(silver_orders_df, "silver", "orders")

        logger.info("Completed transform job: wrote table novalake.silver.orders")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
