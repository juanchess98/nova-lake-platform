"""Transform bronze products into validated silver products."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table
from transformations.bronze_to_silver.common import dedupe_latest, parse_boolean

VALID_CATEGORIES = ["Electronics", "Home", "Fashion", "Sports", "Beauty", "Books", "Toys"]


def standardize_products(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("product_id", F.upper(F.trim(F.col("product_id"))))
        .withColumn("product_name", F.trim(F.col("product_name")))
        .withColumn("category", F.initcap(F.trim(F.col("category"))))
        .withColumn("subcategory", F.initcap(F.trim(F.col("subcategory"))))
        .withColumn("brand", F.trim(F.col("brand")))
        .withColumn("unit_price", F.round(F.col("unit_price").cast("decimal(12,2)"), 2))
        .withColumn("cost", F.round(F.col("cost").cast("decimal(12,2)"), 2))
        .withColumn("created_at", F.to_timestamp("created_at"))
        .withColumn("is_active", parse_boolean("is_active"))
    )


def apply_quality_checks(df: DataFrame) -> DataFrame:
    valid_df = (
        df.filter(F.col("product_id").rlike(r"^PROD\d{6}$"))
        .filter(F.col("product_name").isNotNull())
        .filter(F.col("category").isin(VALID_CATEGORIES))
        .filter(F.col("unit_price").isNotNull() & (F.col("unit_price") > 0))
        .filter(F.col("cost").isNotNull() & (F.col("cost") > 0))
        .filter(F.col("cost") <= F.col("unit_price"))
        .filter(F.col("cost") >= F.round(F.col("unit_price") * F.lit(0.45), 2))
        .filter(F.col("cost") <= F.round(F.col("unit_price") * F.lit(0.75), 2))
        .filter(F.col("created_at").isNotNull())
    )
    return dedupe_latest(valid_df, ["product_id"])


def main() -> None:
    logger = get_logger("novalake.jobs.transform.products_silver")
    spark = create_spark_session("novalake_products_bronze_to_silver")
    logger.info("Starting transform job: bronze.products -> silver.products")

    try:
        bronze_df = spark.table(table_identifier("bronze", "products"))
        silver_df = apply_quality_checks(standardize_products(bronze_df))

        ensure_namespace(spark, "silver")
        write_iceberg_table(silver_df, "silver", "products")
        logger.info("Completed transform job: wrote table novalake.silver.products")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
