"""Build daily revenue gold mart from silver orders."""

from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table


def main() -> None:
    logger = get_logger("novalake.jobs.transform.daily_revenue_gold")
    spark = create_spark_session("novalake_daily_revenue_gold")
    logger.info("Starting transform job: silver.orders -> gold.daily_revenue")

    try:
        silver_orders_df = spark.table(table_identifier("silver", "orders"))

        daily_revenue_df = (
            silver_orders_df.filter(F.col("order_status") == F.lit("completed"))
            .withColumn("order_date", F.to_date("order_timestamp"))
            .groupBy("order_date", "currency")
            .agg(
                F.round(F.sum("total_amount"), 2).alias("daily_revenue"),
                F.countDistinct("order_id").alias("order_count"),
                F.round(F.avg("total_amount"), 2).alias("avg_order_value"),
            )
            .withColumn("_processed_timestamp", F.current_timestamp())
        )

        ensure_namespace(spark, "gold")
        write_iceberg_table(daily_revenue_df, "gold", "daily_revenue")
        logger.info("Completed transform job: wrote table novalake.gold.daily_revenue")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
