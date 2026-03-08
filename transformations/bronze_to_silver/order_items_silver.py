"""Transform bronze order_items into validated silver order_items."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table
from transformations.bronze_to_silver.common import dedupe_latest


def standardize_order_items(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("order_item_id", F.upper(F.trim(F.col("order_item_id"))))
        .withColumn("order_id", F.upper(F.trim(F.col("order_id"))))
        .withColumn("product_id", F.upper(F.trim(F.col("product_id"))))
        .withColumn("quantity", F.col("quantity").cast("int"))
        .withColumn("unit_price", F.round(F.col("unit_price").cast("decimal(12,2)"), 2))
        .withColumn("discount_amount", F.round(F.col("discount_amount").cast("decimal(12,2)"), 2))
        .withColumn("line_total", F.round(F.col("line_total").cast("decimal(12,2)"), 2))
    )


def apply_quality_checks(df: DataFrame) -> DataFrame:
    valid_df = (
        df.filter(F.col("order_item_id").rlike(r"^ITEM\d{8}$"))
        .filter(F.col("order_id").rlike(r"^ORD\d{8}$"))
        .filter(F.col("product_id").rlike(r"^PROD\d{6}$"))
        .filter(F.col("quantity").between(1, 5))
        .filter(F.col("unit_price") > 0)
        .filter(F.col("discount_amount") >= 0)
        .filter(F.round((F.col("quantity") * F.col("unit_price")) - F.col("discount_amount"), 2) == F.col("line_total"))
    )
    return dedupe_latest(valid_df, ["order_item_id"])


def enforce_referential_integrity(
    order_items_df: DataFrame,
    orders_df: DataFrame,
    products_df: DataFrame,
) -> DataFrame:
    with_orders = order_items_df.join(orders_df.select("order_id"), on="order_id", how="inner")
    return with_orders.join(products_df.select("product_id"), on="product_id", how="inner")


def enforce_order_subtotal_consistency(order_items_df: DataFrame, orders_df: DataFrame) -> DataFrame:
    order_item_subtotals = (
        order_items_df.groupBy("order_id")
        .agg(F.round(F.sum("line_total"), 2).alias("calc_subtotal"))
    )

    valid_orders = (
        orders_df.select("order_id", "subtotal_amount")
        .join(order_item_subtotals, on="order_id", how="inner")
        .filter(F.col("subtotal_amount") == F.col("calc_subtotal"))
        .select("order_id")
    )

    return order_items_df.join(valid_orders, on="order_id", how="inner")


def main() -> None:
    logger = get_logger("novalake.jobs.transform.order_items_silver")
    spark = create_spark_session("novalake_order_items_bronze_to_silver")
    logger.info("Starting transform job: bronze.order_items -> silver.order_items")

    try:
        bronze_df = spark.table(table_identifier("bronze", "order_items"))
        silver_orders_df = spark.table(table_identifier("silver", "orders"))
        silver_products_df = spark.table(table_identifier("silver", "products"))

        standardized_df = standardize_order_items(bronze_df)
        quality_df = apply_quality_checks(standardized_df)
        ri_df = enforce_referential_integrity(quality_df, silver_orders_df, silver_products_df)
        silver_df = enforce_order_subtotal_consistency(ri_df, silver_orders_df)

        ensure_namespace(spark, "silver")
        write_iceberg_table(silver_df, "silver", "order_items")
        logger.info("Completed transform job: wrote table novalake.silver.order_items")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
