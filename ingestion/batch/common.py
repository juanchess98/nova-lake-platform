"""Shared ingestion helpers for loading raw CSV datasets into Bronze."""

from core.spark import (
    add_ingestion_metadata,
    create_spark_session,
    ensure_namespace,
    get_logger,
    read_raw_csv,
    write_iceberg_table,
)


def ingest_raw_dataset_to_bronze(dataset_name: str) -> None:
    """Load one raw dataset from data/raw into the matching bronze Iceberg table."""
    logger = get_logger(f"novalake.jobs.ingestion.{dataset_name}_bronze")
    spark = create_spark_session(f"novalake_load_{dataset_name}_to_bronze")
    logger.info("Starting ingestion job: raw %s -> bronze.%s", dataset_name, dataset_name)

    try:
        raw_df = read_raw_csv(spark, dataset_name)
        bronze_df = add_ingestion_metadata(raw_df)

        ensure_namespace(spark, "bronze")
        write_iceberg_table(bronze_df, "bronze", dataset_name)

        logger.info("Completed ingestion job: wrote table novalake.bronze.%s", dataset_name)
    finally:
        spark.stop()
        logger.info("Spark session stopped")
