"""Build daily revenue gold mart from silver orders."""

from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, table_identifier

REVENUE_STATUSES = ["paid", "shipped", "completed"]


def main() -> None:
    spark = create_spark_session("novalake_daily_revenue_gold")

    silver_orders_df = spark.table(table_identifier("silver", "orders"))

    daily_revenue_df = (
        silver_orders_df.filter(F.col("order_status").isin(REVENUE_STATUSES))
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

    (
        daily_revenue_df.writeTo(table_identifier("gold", "daily_revenue"))
        .using("iceberg")
        .tableProperty("format-version", "2")
        .createOrReplace()
    )

    spark.stop()


if __name__ == "__main__":
    main()
