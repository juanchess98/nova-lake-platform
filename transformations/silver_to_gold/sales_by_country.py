"""Build sales by country gold mart from silver orders and customers."""

from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table


def main() -> None:
    logger = get_logger("novalake.jobs.transform.sales_by_country_gold")
    spark = create_spark_session("novalake_sales_by_country_gold")
    logger.info("Starting transform job: silver orders+customers -> gold.sales_by_country")

    try:
        orders_df = spark.table(table_identifier("silver", "orders")).filter(F.col("order_status") == "completed")
        customers_df = spark.table(table_identifier("silver", "customers")).select("customer_id", "country")

        sales_df = (
            orders_df.join(customers_df, on="customer_id", how="inner")
            .withColumn("order_date", F.to_date("order_timestamp"))
            .groupBy("order_date", "country", "currency")
            .agg(
                F.countDistinct("order_id").alias("order_count"),
                F.round(F.sum("total_amount"), 2).alias("gross_revenue"),
                F.round(F.avg("total_amount"), 2).alias("avg_order_value"),
            )
            .withColumn("_processed_timestamp", F.current_timestamp())
        )

        ensure_namespace(spark, "gold")
        write_iceberg_table(sales_df, "gold", "sales_by_country")
        logger.info("Completed transform job: wrote table novalake.gold.sales_by_country")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
