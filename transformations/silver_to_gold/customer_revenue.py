"""Build customer revenue gold mart from silver orders and customers."""

from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table


def main() -> None:
    logger = get_logger("novalake.jobs.transform.customer_revenue_gold")
    spark = create_spark_session("novalake_customer_revenue_gold")
    logger.info("Starting transform job: silver orders+customers -> gold.customer_revenue")

    try:
        orders_df = spark.table(table_identifier("silver", "orders")).filter(F.col("order_status") == "completed")
        customers_df = spark.table(table_identifier("silver", "customers")).select(
            "customer_id", "email", "first_name", "last_name", "country", "customer_segment", "is_active"
        )

        customer_revenue_df = (
            orders_df.join(customers_df, on="customer_id", how="inner")
            .groupBy(
                "customer_id", "email", "first_name", "last_name", "country", "customer_segment", "is_active", "currency"
            )
            .agg(
                F.countDistinct("order_id").alias("completed_orders"),
                F.round(F.sum("total_amount"), 2).alias("lifetime_revenue"),
                F.round(F.avg("total_amount"), 2).alias("avg_order_value"),
                F.max("order_timestamp").alias("last_order_timestamp"),
            )
            .withColumn("_processed_timestamp", F.current_timestamp())
        )

        ensure_namespace(spark, "gold")
        write_iceberg_table(customer_revenue_df, "gold", "customer_revenue")
        logger.info("Completed transform job: wrote table novalake.gold.customer_revenue")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
