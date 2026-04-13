"""Basic structural checks for NovaLake project conventions."""

from pathlib import Path

from core.config import (
    CATALOG_BACKEND,
    CATALOG_BACKEND_NESSIE,
    RAW_DATA_DIR,
    STORAGE_BACKEND_S3,
    WAREHOUSE_DIR,
    spark_runtime_config,
    spark_sql_cli_config,
    warehouse_uri,
)


def test_data_directories_exist() -> None:
    assert RAW_DATA_DIR.exists(), "Raw data directory is missing."
    assert WAREHOUSE_DIR.exists(), "Warehouse directory is missing."


def test_compose_file_exists() -> None:
    compose_file = Path("infra/docker-compose.yml")
    assert compose_file.exists(), "Compose file should live under infra/."


def test_spark_image_dockerfile_exists() -> None:
    spark_dockerfile = Path("infra/spark/Dockerfile")
    assert spark_dockerfile.exists(), "Custom Spark image Dockerfile is missing."
    lab_dockerfile = Path("infra/lab/Dockerfile")
    assert lab_dockerfile.exists(), "Notebook lab Dockerfile is missing."
    lab_kernel = Path("infra/lab/pyspark_novalake_kernel.json")
    assert lab_kernel.exists(), "Notebook lab PySpark kernel spec is missing."


def test_job_runner_scripts_exist() -> None:
    assert Path("scripts/run_job.sh").exists(), "Bash runner script is missing."
    assert Path("scripts/run_job.ps1").exists(), "PowerShell runner script is missing."
    assert Path("scripts/run_lab.sh").exists(), "Bash notebook lab script is missing."
    assert Path("scripts/run_lab.ps1").exists(), "PowerShell notebook lab script is missing."
    assert Path("scripts/lab_health.sh").exists(), "Bash notebook lab health script is missing."
    assert Path("scripts/lab_health.ps1").exists(), "PowerShell notebook lab health script is missing."
    assert Path("scripts/sql_shell.sh").exists(), "Bash SQL shell script is missing."
    assert Path("scripts/sql_shell.ps1").exists(), "PowerShell SQL shell script is missing."
    assert Path("scripts/start_notebook_lab.sh").exists(), "Notebook lab startup script is missing."


def test_notebook_templates_exist() -> None:
    assert Path("notebooks/README.md").exists(), "Notebook README is missing."
    assert Path("notebooks/01_lakehouse_exploration.ipynb").exists(), "Starter notebook is missing."


def test_architecture_docs_exist() -> None:
    assert Path("docs/architecture.md").exists(), "Architecture document is missing."
    assert Path("docs/roadmap.md").exists(), "Roadmap document is missing."
    assert Path("docs/architecture/module_02_storage_evolution.md").exists(), (
        "Module 2 architecture document is missing."
    )
    assert Path("docs/architecture/module_03_catalog_metadata_foundation.md").exists(), (
        "Module 3 architecture document is missing."
    )
    assert Path("docs/diagrams/module1-v1.mmd").exists(), "Module 1 architecture diagram is missing."


def test_module_2_warehouse_defaults_to_s3() -> None:
    assert STORAGE_BACKEND_S3 == "s3_compatible"
    assert warehouse_uri().startswith("s3a://"), "Module 2 should default to object storage."


def test_module_3_catalog_defaults_to_nessie() -> None:
    assert CATALOG_BACKEND_NESSIE == "nessie"
    assert CATALOG_BACKEND == CATALOG_BACKEND_NESSIE


def test_shared_runtime_config_uses_nessie_without_catalog_fallback() -> None:
    runtime_config = spark_runtime_config()

    assert "spark.sql.catalogImplementation" not in runtime_config
    assert (
        runtime_config["spark.sql.catalog.novalake.catalog-impl"]
        == "org.apache.iceberg.nessie.NessieCatalog"
    )


def test_spark_sql_cli_config_keeps_local_hive_suppression() -> None:
    cli_config = spark_sql_cli_config()

    assert cli_config["spark.sql.catalogImplementation"] == "in-memory"
    assert (
        cli_config["spark.sql.catalog.novalake.catalog-impl"]
        == "org.apache.iceberg.nessie.NessieCatalog"
    )
