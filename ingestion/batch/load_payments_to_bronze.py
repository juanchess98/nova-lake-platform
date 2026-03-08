"""Batch ingestion job for raw payments into bronze layer."""

from ingestion.batch.common import ingest_raw_dataset_to_bronze


if __name__ == "__main__":
    ingest_raw_dataset_to_bronze("payments")
