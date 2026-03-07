"""Basic structural checks for local project conventions."""

from pathlib import Path

from core.config import RAW_DATA_DIR, WAREHOUSE_DIR


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


def test_notebook_templates_exist() -> None:
    assert Path("notebooks/README.md").exists(), "Notebook README is missing."
    assert Path("notebooks/01_lakehouse_exploration.ipynb").exists(), "Starter notebook is missing."
