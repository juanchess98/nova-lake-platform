"""Transform bronze customers into validated silver customers."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table
from transformations.bronze_to_silver.common import dedupe_latest, parse_boolean

VALID_COUNTRIES = ["US", "CA", "MX", "CO", "ES", "BR", "AR", "CL"]
VALID_SEGMENTS = ["Standard", "Premium", "VIP"]


def standardize_customers(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("customer_id", F.upper(F.trim(F.col("customer_id"))))
        .withColumn("email", F.lower(F.trim(F.col("email"))))
        .withColumn("first_name", F.initcap(F.trim(F.col("first_name"))))
        .withColumn("last_name", F.initcap(F.trim(F.col("last_name"))))
        .withColumn("country", F.upper(F.trim(F.col("country"))))
        .withColumn("city", F.initcap(F.trim(F.col("city"))))
        .withColumn("signup_date", F.to_date("signup_date"))
        .withColumn("customer_segment", F.initcap(F.trim(F.col("customer_segment"))))
        .withColumn("is_active", parse_boolean("is_active"))
    )


def apply_quality_checks(df: DataFrame) -> DataFrame:
    valid_df = (
        df.filter(F.col("customer_id").rlike(r"^CUST\d{6}$"))
        .filter(F.col("email").isNotNull())
        .filter(F.col("signup_date").isNotNull())
        .filter(F.col("country").isin(VALID_COUNTRIES))
        .filter(F.col("customer_segment").isin(VALID_SEGMENTS))
    )

    return dedupe_latest(valid_df, ["customer_id"])


def keep_unique_email(df: DataFrame) -> DataFrame:
    # Keep one deterministic customer per email to preserve uniqueness in Silver.
    email_rank = F.row_number().over(
        Window.partitionBy("email").orderBy(
            F.col("_ingestion_timestamp").desc_nulls_last(),
            F.col("customer_id"),
        )
    )
    return df.withColumn("_email_rank", email_rank).filter(F.col("_email_rank") == 1).drop("_email_rank")


def main() -> None:
    logger = get_logger("novalake.jobs.transform.customers_silver")
    spark = create_spark_session("novalake_customers_bronze_to_silver")
    logger.info("Starting transform job: bronze.customers -> silver.customers")

    try:
        bronze_df = spark.table(table_identifier("bronze", "customers"))
        standardized_df = standardize_customers(bronze_df)
        clean_df = apply_quality_checks(standardized_df)
        silver_df = keep_unique_email(clean_df)

        ensure_namespace(spark, "silver")
        write_iceberg_table(silver_df, "silver", "customers")
        logger.info("Completed transform job: wrote table novalake.silver.customers")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
