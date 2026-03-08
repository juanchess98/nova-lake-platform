"""Shared helpers for Bronze to Silver transformation jobs."""

from typing import List

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def dedupe_latest(df: DataFrame, key_columns: List[str]) -> DataFrame:
    """Keep the latest record per business key based on ingestion metadata."""
    row_number_window = Window.partitionBy(*key_columns).orderBy(
        F.col("_ingestion_timestamp").desc_nulls_last(),
        F.col("_source_file").desc_nulls_last(),
    )
    return (
        df.withColumn("_row_num", F.row_number().over(row_number_window))
        .filter(F.col("_row_num") == 1)
        .drop("_row_num")
    )


def parse_boolean(column_name: str):
    """Parse truthy/falsy textual values from CSV into Spark booleans."""
    normalized = F.lower(F.trim(F.col(column_name)))
    return (
        F.when(normalized.isin("true", "1", "yes", "y"), F.lit(True))
        .when(normalized.isin("false", "0", "no", "n"), F.lit(False))
        .otherwise(F.lit(None).cast("boolean"))
    )
