"""Build shipment delivery summary gold mart from silver shipments."""

from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table


def main() -> None:
    logger = get_logger("novalake.jobs.transform.shipment_delivery_summary_gold")
    spark = create_spark_session("novalake_shipment_delivery_summary_gold")
    logger.info("Starting transform job: silver.shipments -> gold.shipment_delivery_summary")

    try:
        shipments_df = spark.table(table_identifier("silver", "shipments"))

        shipment_summary_df = (
            shipments_df.withColumn("shipment_date", F.to_date("shipment_timestamp"))
            .withColumn(
                "delivery_hours",
                F.when(
                    F.col("delivery_timestamp").isNotNull(),
                    (F.unix_timestamp("delivery_timestamp") - F.unix_timestamp("shipment_timestamp")) / 3600.0,
                ),
            )
            .groupBy("shipment_date", "shipping_country", "carrier")
            .agg(
                F.count("shipment_id").alias("shipment_count"),
                F.sum(F.when(F.col("shipment_status") == "delivered", 1).otherwise(0)).alias("delivered_count"),
                F.sum(F.when(F.col("shipment_status") == "shipped", 1).otherwise(0)).alias("in_transit_count"),
                F.sum(F.when(F.col("shipment_status") == "delayed", 1).otherwise(0)).alias("delayed_count"),
                F.round(F.avg("delivery_hours"), 2).alias("avg_delivery_hours"),
            )
            .withColumn(
                "delivery_rate",
                F.round(F.col("delivered_count") / F.when(F.col("shipment_count") == 0, F.lit(1)).otherwise(F.col("shipment_count")), 4),
            )
            .withColumn("_processed_timestamp", F.current_timestamp())
        )

        ensure_namespace(spark, "gold")
        write_iceberg_table(shipment_summary_df, "gold", "shipment_delivery_summary")
        logger.info("Completed transform job: wrote table novalake.gold.shipment_delivery_summary")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
