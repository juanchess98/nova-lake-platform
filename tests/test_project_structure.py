"""Basic structural checks for local project conventions."""

from pathlib import Path

from core.config import RAW_DATA_DIR, WAREHOUSE_DIR


def test_data_directories_exist() -> None:
    assert RAW_DATA_DIR.exists(), "Raw data directory is missing."
    assert WAREHOUSE_DIR.exists(), "Warehouse directory is missing."


def test_compose_file_exists() -> None:
    compose_file = Path("infra/docker-compose.yml")
    assert compose_file.exists(), "Compose file should live under infra/."
