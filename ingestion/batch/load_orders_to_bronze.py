"""Batch ingestion job for raw orders into bronze layer."""

from core.spark import (
    add_ingestion_metadata,
    create_spark_session,
    ensure_namespace,
    read_raw_csv,
    table_identifier,
)


def main() -> None:
    spark = create_spark_session("novalake_load_orders_to_bronze")

    orders_raw_df = read_raw_csv(spark, "orders")
    bronze_orders_df = add_ingestion_metadata(orders_raw_df)

    ensure_namespace(spark, "bronze")

    (
        bronze_orders_df.writeTo(table_identifier("bronze", "orders"))
        .using("iceberg")
        .tableProperty("format-version", "2")
        .createOrReplace()
    )

    spark.stop()


if __name__ == "__main__":
    main()
