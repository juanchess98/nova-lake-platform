"""Batch ingestion job for raw orders into bronze layer."""

from core.spark import (
    add_ingestion_metadata,
    create_spark_session,
    ensure_namespace,
    get_logger,
    read_raw_csv,
    write_iceberg_table,
)


def main() -> None:
    logger = get_logger("novalake.jobs.ingestion.orders_bronze")
    spark = create_spark_session("novalake_load_orders_to_bronze")
    logger.info("Starting ingestion job: raw orders -> bronze.orders")

    try:
        orders_raw_df = read_raw_csv(spark, "orders")
        bronze_orders_df = add_ingestion_metadata(orders_raw_df)

        ensure_namespace(spark, "bronze")
        write_iceberg_table(bronze_orders_df, "bronze", "orders")

        logger.info("Completed ingestion job: wrote table novalake.bronze.orders")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
