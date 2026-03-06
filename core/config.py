"""Central configuration for NovaLake Module 1."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
WAREHOUSE_DIR = DATA_DIR / "warehouse"

ICEBERG_CATALOG = "novalake"
MEDALLION_LAYERS = ("bronze", "silver", "gold")
