"""Build top products gold mart from silver order_items, orders, and products."""

from pyspark.sql import functions as F
from pyspark.sql.window import Window

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table


def main() -> None:
    logger = get_logger("novalake.jobs.transform.top_products_gold")
    spark = create_spark_session("novalake_top_products_gold")
    logger.info("Starting transform job: silver order_items+orders+products -> gold.top_products")

    try:
        orders_df = spark.table(table_identifier("silver", "orders")).filter(F.col("order_status") == "completed")
        items_df = spark.table(table_identifier("silver", "order_items"))
        products_df = spark.table(table_identifier("silver", "products")).select(
            "product_id", "product_name", "category", "subcategory", "brand"
        )

        product_sales_df = (
            items_df.join(orders_df.select("order_id", "currency"), on="order_id", how="inner")
            .join(products_df, on="product_id", how="inner")
            .groupBy("product_id", "product_name", "category", "subcategory", "brand", "currency")
            .agg(
                F.sum("quantity").alias("units_sold"),
                F.round(F.sum("line_total"), 2).alias("product_revenue"),
                F.countDistinct("order_id").alias("orders_count"),
            )
            .withColumn("revenue_rank", F.dense_rank().over(Window.orderBy(F.col("product_revenue").desc())))
            .filter(F.col("revenue_rank") <= 100)
            .withColumn("_processed_timestamp", F.current_timestamp())
        )

        ensure_namespace(spark, "gold")
        write_iceberg_table(product_sales_df, "gold", "top_products")
        logger.info("Completed transform job: wrote table novalake.gold.top_products")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
