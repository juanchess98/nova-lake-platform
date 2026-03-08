"""Central configuration for NovaLake Platform (Module 1 baseline)."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
WAREHOUSE_DIR = DATA_DIR / "warehouse"

ICEBERG_CATALOG = "novalake"
MEDALLION_LAYERS = ("bronze", "silver", "gold")

# Module 1 intentionally uses local filesystem storage only.
STORAGE_BACKEND_LOCAL = "local_filesystem"
STORAGE_BACKEND = os.getenv("NOVALAKE_STORAGE_BACKEND", STORAGE_BACKEND_LOCAL)


def warehouse_uri() -> str:
    """Return the warehouse URI used by the active storage backend."""
    if STORAGE_BACKEND == STORAGE_BACKEND_LOCAL:
        WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
        return WAREHOUSE_DIR.as_posix()

    raise ValueError(
        "Unsupported storage backend configured: "
        f"'{STORAGE_BACKEND}'. Module 1 supports only '{STORAGE_BACKEND_LOCAL}'."
    )


def iceberg_catalog_config() -> dict[str, str]:
    """Build Iceberg catalog settings for Spark sessions."""
    return {
        f"spark.sql.catalog.{ICEBERG_CATALOG}": "org.apache.iceberg.spark.SparkCatalog",
        f"spark.sql.catalog.{ICEBERG_CATALOG}.type": "hadoop",
        f"spark.sql.catalog.{ICEBERG_CATALOG}.warehouse": warehouse_uri(),
    }
