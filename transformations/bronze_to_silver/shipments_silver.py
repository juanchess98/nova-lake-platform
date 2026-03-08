"""Transform bronze shipments into validated silver shipments."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table
from transformations.bronze_to_silver.common import dedupe_latest

VALID_STATUSES = ["shipped", "delivered", "delayed"]
VALID_CARRIERS = ["DHL", "FedEx", "UPS", "USPS", "Servientrega", "Correos"]
VALID_COUNTRIES = ["US", "CA", "MX", "CO", "ES", "BR", "AR", "CL"]


def standardize_shipments(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("shipment_id", F.upper(F.trim(F.col("shipment_id"))))
        .withColumn("order_id", F.upper(F.trim(F.col("order_id"))))
        .withColumn("shipment_timestamp", F.to_timestamp("shipment_timestamp"))
        .withColumn("delivery_timestamp", F.to_timestamp("delivery_timestamp"))
        .withColumn("shipment_status", F.lower(F.trim(F.col("shipment_status"))))
        .withColumn("carrier", F.trim(F.col("carrier")))
        .withColumn("shipping_country", F.upper(F.trim(F.col("shipping_country"))))
    )


def apply_quality_checks(df: DataFrame) -> DataFrame:
    valid_df = (
        df.filter(F.col("shipment_id").rlike(r"^SHP\d{8}$"))
        .filter(F.col("order_id").rlike(r"^ORD\d{8}$"))
        .filter(F.col("shipment_timestamp").isNotNull())
        .filter(F.col("shipment_status").isin(VALID_STATUSES))
        .filter(F.col("carrier").isin(VALID_CARRIERS))
        .filter(F.col("shipping_country").isin(VALID_COUNTRIES))
        .filter(
            F.col("delivery_timestamp").isNull()
            | (F.col("delivery_timestamp") >= F.col("shipment_timestamp"))
        )
    )
    return dedupe_latest(valid_df, ["shipment_id"])


def enforce_order_referential_integrity(shipments_df: DataFrame, orders_df: DataFrame) -> DataFrame:
    return (
        shipments_df.join(
            orders_df.select("order_id", "order_timestamp", "order_status"),
            on="order_id",
            how="inner",
        )
        .filter(F.col("order_status") != F.lit("cancelled"))
        .filter(F.col("shipment_timestamp") >= F.col("order_timestamp"))
    )


def main() -> None:
    logger = get_logger("novalake.jobs.transform.shipments_silver")
    spark = create_spark_session("novalake_shipments_bronze_to_silver")
    logger.info("Starting transform job: bronze.shipments -> silver.shipments")

    try:
        bronze_df = spark.table(table_identifier("bronze", "shipments"))
        silver_orders_df = spark.table(table_identifier("silver", "orders"))

        standardized_df = standardize_shipments(bronze_df)
        quality_df = apply_quality_checks(standardized_df)
        joined_df = enforce_order_referential_integrity(quality_df, silver_orders_df)

        silver_df = joined_df.select(
            "shipment_id",
            "order_id",
            "shipment_timestamp",
            "delivery_timestamp",
            "shipment_status",
            "carrier",
            "shipping_country",
            "_ingestion_timestamp",
            "_source_file",
        )

        ensure_namespace(spark, "silver")
        write_iceberg_table(silver_df, "silver", "shipments")
        logger.info("Completed transform job: wrote table novalake.silver.shipments")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
