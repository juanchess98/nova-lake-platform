# Architecture - Module 1 (Lakehouse Foundation)

## Purpose

Establish a local, reproducible lakehouse baseline with engineering conventions that support future platform modules without refactoring the foundation.

## Design Principles

- Modular structure by responsibility
- Layer isolation through medallion namespaces
- Shared runtime configuration for consistency
- Lightweight quality controls before business aggregation
- Local-first execution with deterministic sample data

## Logical Layers

- Bronze (`novalake.bronze`)
  - ingestion-aligned representation
  - includes technical lineage fields (`_ingestion_timestamp`, `_source_file`)
- Silver (`novalake.silver`)
  - standardized naming and datatypes
  - basic quality filters and deterministic deduplication
- Gold (`novalake.gold`)
  - business-ready aggregates
  - current output: `daily_revenue`

## Runtime Components

- Spark jobs
  - `ingestion/batch/load_orders_to_bronze.py`
  - `transformations/bronze_to_silver/orders_silver.py`
  - `transformations/silver_to_gold/daily_revenue.py`
- Shared modules
  - `core/config.py`: platform constants and paths
  - `core/spark.py`: Spark session factory, table identifiers, namespace helpers
- Storage
  - Raw files: `data/raw/*.csv`
  - Iceberg warehouse: `data/warehouse`
- Metadata contract
  - `metadata/datasets.yaml`

## Local Topology

- `postgres`: operational system seed for upcoming ingestion modules
- `spark-master` and `spark-worker`: local processing runtime

## Current Data Flow

1. Ingest `orders.csv` into `novalake.bronze.orders`
2. Apply standardization + quality checks into `novalake.silver.orders`
3. Aggregate to `novalake.gold.daily_revenue`

## Extension Hooks

- Ingestion domain split (`ingestion/batch`) can add `ingestion/streaming` for Kafka/Debezium
- Transformation domain split can add dbt-compatible models in a separate module
- Shared config/helpers avoid hardcoded paths across jobs
- ADR workflow (`docs/decisions.md`) preserves architecture rationale as scope expands
