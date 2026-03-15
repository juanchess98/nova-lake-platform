"""Central configuration for NovaLake Platform storage and Spark runtime."""

import os
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
WAREHOUSE_DIR = DATA_DIR / "warehouse"

ICEBERG_CATALOG = "novalake"
MEDALLION_LAYERS = ("bronze", "silver", "gold")

STORAGE_BACKEND_LOCAL = "local_filesystem"
STORAGE_BACKEND_S3 = "s3_compatible"
STORAGE_BACKEND = os.getenv("NOVALAKE_STORAGE_BACKEND", STORAGE_BACKEND_S3)

SPARK_SQL_EXTENSIONS = "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"

S3_ENDPOINT = os.getenv("NOVALAKE_S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("NOVALAKE_S3_ACCESS_KEY", "novalake")
S3_SECRET_KEY = os.getenv("NOVALAKE_S3_SECRET_KEY", "novalake123")
S3_BUCKET = os.getenv("NOVALAKE_S3_BUCKET", "novalake-lakehouse")
S3_WAREHOUSE_PREFIX = os.getenv("NOVALAKE_S3_WAREHOUSE_PREFIX", "warehouse").strip("/")
S3_PATH_STYLE_ACCESS = os.getenv("NOVALAKE_S3_PATH_STYLE_ACCESS", "true").lower()


def _s3_endpoint_authority() -> str:
    parsed = urlparse(S3_ENDPOINT)
    return parsed.netloc or parsed.path


def _s3_ssl_enabled() -> str:
    parsed = urlparse(S3_ENDPOINT)
    if parsed.scheme:
        return str(parsed.scheme.lower() == "https").lower()
    return "false"


def warehouse_uri() -> str:
    """Return the warehouse URI used by the active storage backend."""
    if STORAGE_BACKEND == STORAGE_BACKEND_LOCAL:
        WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
        return WAREHOUSE_DIR.as_posix()

    if STORAGE_BACKEND == STORAGE_BACKEND_S3:
        return f"s3a://{S3_BUCKET}/{S3_WAREHOUSE_PREFIX}"

    raise ValueError(
        "Unsupported storage backend configured: "
        f"'{STORAGE_BACKEND}'. Expected one of: "
        f"'{STORAGE_BACKEND_LOCAL}', '{STORAGE_BACKEND_S3}'."
    )


def iceberg_catalog_config() -> Dict[str, str]:
    """Build Iceberg catalog settings for Spark sessions."""
    config = {
        f"spark.sql.catalog.{ICEBERG_CATALOG}": "org.apache.iceberg.spark.SparkCatalog",
        f"spark.sql.catalog.{ICEBERG_CATALOG}.type": "hadoop",
        f"spark.sql.catalog.{ICEBERG_CATALOG}.warehouse": warehouse_uri(),
    }

    if STORAGE_BACKEND == STORAGE_BACKEND_S3:
        config.update(
            {
                "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
                "spark.hadoop.fs.s3a.endpoint": _s3_endpoint_authority(),
                "spark.hadoop.fs.s3a.access.key": S3_ACCESS_KEY,
                "spark.hadoop.fs.s3a.secret.key": S3_SECRET_KEY,
                "spark.hadoop.fs.s3a.path.style.access": S3_PATH_STYLE_ACCESS,
                "spark.hadoop.fs.s3a.connection.ssl.enabled": _s3_ssl_enabled(),
                "spark.hadoop.fs.s3a.aws.credentials.provider": (
                    "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
                ),
            }
        )

    return config


def spark_runtime_config() -> Dict[str, str]:
    """Build shared Spark runtime settings for NovaLake sessions."""
    return {
        "spark.sql.catalogImplementation": "in-memory",
        "spark.sql.extensions": SPARK_SQL_EXTENSIONS,
        **iceberg_catalog_config(),
    }
