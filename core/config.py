"""Central configuration for NovaLake Platform catalog, storage, and Spark runtime."""

import os
from pathlib import Path
from typing import Dict, List
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

CATALOG_BACKEND_HADOOP = "hadoop"
CATALOG_BACKEND_NESSIE = "nessie"
CATALOG_BACKEND = os.getenv("NOVALAKE_CATALOG_BACKEND", CATALOG_BACKEND_NESSIE)

SPARK_SQL_EXTENSIONS = "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
SPARK_SQL_CLI_CATALOG_IMPLEMENTATION = "in-memory"

S3_ENDPOINT = os.getenv("NOVALAKE_S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("NOVALAKE_S3_ACCESS_KEY", "novalake")
S3_SECRET_KEY = os.getenv("NOVALAKE_S3_SECRET_KEY", "novalake123")
S3_BUCKET = os.getenv("NOVALAKE_S3_BUCKET", "novalake-lakehouse")
S3_WAREHOUSE_PREFIX = os.getenv("NOVALAKE_S3_WAREHOUSE_PREFIX", "warehouse").strip("/")
S3_PATH_STYLE_ACCESS = os.getenv("NOVALAKE_S3_PATH_STYLE_ACCESS", "true").lower()

CATALOG_URI = os.getenv("NOVALAKE_CATALOG_URI", "http://nessie:19120/api/v1")
CATALOG_REF = os.getenv("NOVALAKE_CATALOG_REF", "main")
CATALOG_AUTH_TYPE = os.getenv("NOVALAKE_CATALOG_AUTH_TYPE", "NONE")


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


def _base_catalog_config() -> Dict[str, str]:
    return {
        f"spark.sql.catalog.{ICEBERG_CATALOG}": "org.apache.iceberg.spark.SparkCatalog",
        f"spark.sql.catalog.{ICEBERG_CATALOG}.warehouse": warehouse_uri(),
    }


def _nessie_catalog_config() -> Dict[str, str]:
    return {
        **_base_catalog_config(),
        f"spark.sql.catalog.{ICEBERG_CATALOG}.catalog-impl": (
            "org.apache.iceberg.nessie.NessieCatalog"
        ),
        f"spark.sql.catalog.{ICEBERG_CATALOG}.uri": CATALOG_URI,
        f"spark.sql.catalog.{ICEBERG_CATALOG}.ref": CATALOG_REF,
        f"spark.sql.catalog.{ICEBERG_CATALOG}.authentication.type": CATALOG_AUTH_TYPE,
    }


def iceberg_catalog_config() -> Dict[str, str]:
    """Build Iceberg catalog settings for Spark sessions."""
    if CATALOG_BACKEND == CATALOG_BACKEND_HADOOP:
        config = {
            **_base_catalog_config(),
            f"spark.sql.catalog.{ICEBERG_CATALOG}.type": "hadoop",
        }
    elif CATALOG_BACKEND == CATALOG_BACKEND_NESSIE:
        config = _nessie_catalog_config()
    else:
        raise ValueError(
            "Unsupported catalog backend configured: "
            f"'{CATALOG_BACKEND}'. Expected one of: "
            f"'{CATALOG_BACKEND_HADOOP}', '{CATALOG_BACKEND_NESSIE}'."
        )

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
        "spark.sql.extensions": SPARK_SQL_EXTENSIONS,
        **iceberg_catalog_config(),
    }


def spark_sql_cli_config() -> Dict[str, str]:
    """Build spark-sql CLI settings, including local Hive metastore suppression."""
    return {
        **spark_runtime_config(),
        "spark.sql.catalogImplementation": SPARK_SQL_CLI_CATALOG_IMPLEMENTATION,
    }


def spark_conf_cli_args(include_spark_sql_cli_overrides: bool = False) -> List[str]:
    """Return Spark CLI args as alternating ``--conf`` and ``key=value`` entries."""
    args: List[str] = []
    config = (
        spark_sql_cli_config()
        if include_spark_sql_cli_overrides
        else spark_runtime_config()
    )

    for key, value in config.items():
        args.extend(["--conf", f"{key}={value}"])
    return args
