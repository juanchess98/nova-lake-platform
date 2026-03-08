"""Shared Spark helpers for NovaLake Platform jobs."""

import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from core.config import (
    ICEBERG_CATALOG,
    MEDALLION_LAYERS,
    RAW_DATA_DIR,
    iceberg_catalog_config,
)

LOGGER_NAME = "novalake.jobs"
ICEBERG_FORMAT_VERSION = "2"


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    """Return a logger configured for concise job execution messages."""
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    return logging.getLogger(name)


def table_identifier(layer: str, table_name: str) -> str:
    """Build a fully-qualified table name for the configured Iceberg catalog."""
    if layer not in MEDALLION_LAYERS:
        valid_layers = ", ".join(MEDALLION_LAYERS)
        raise ValueError(f"Unsupported layer '{layer}'. Expected one of: {valid_layers}.")
    return f"{ICEBERG_CATALOG}.{layer}.{table_name}"


def ensure_namespace(spark: SparkSession, layer: str) -> None:
    """Ensure a medallion namespace exists."""
    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {ICEBERG_CATALOG}.{layer}")


def read_raw_csv(spark: SparkSession, dataset_name: str) -> DataFrame:
    """Read a raw CSV file from the canonical raw data directory."""
    input_path = RAW_DATA_DIR / f"{dataset_name}.csv"
    if not input_path.exists():
        raise FileNotFoundError(f"Raw dataset not found: {input_path}")

    return (
        spark.read.option("header", True)
        .option("inferSchema", False)
        .csv(input_path.as_posix())
    )


def add_ingestion_metadata(df: DataFrame) -> DataFrame:
    """Attach technical lineage metadata columns used in Bronze."""
    return (
        df.withColumn("_ingestion_timestamp", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
    )


def create_spark_session(app_name: str) -> SparkSession:
    """Create a Spark session configured for local Iceberg catalogs."""
    builder = SparkSession.builder.appName(app_name).config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )

    for key, value in iceberg_catalog_config().items():
        builder = builder.config(key, value)

    return builder.getOrCreate()


def write_iceberg_table(df: DataFrame, layer: str, table_name: str) -> None:
    """Write a DataFrame to an Iceberg table using module defaults."""
    (
        df.writeTo(table_identifier(layer, table_name))
        .using("iceberg")
        .tableProperty("format-version", ICEBERG_FORMAT_VERSION)
        .createOrReplace()
    )
