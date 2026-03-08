# Architecture - Module 1 Baseline (Lakehouse Foundation)

## Purpose

Module 1 is the NovaLake baseline architecture: a local-first lakehouse that is fully operational, reproducible, and ready to evolve without foundation redesign.

## Baseline Principles

- Local-first reproducibility over early infrastructure complexity
- Explicit medallion layering (`bronze`, `silver`, `gold`)
- Shared Spark/config utilities for consistency across jobs
- Deterministic synthetic data generation for repeatable outcomes
- Clear path to future storage and ingestion evolution

## Runtime Components

- Spark jobs
  - Bronze ingestion (`ingestion/batch/load_*_to_bronze.py`) for all six entities
  - Silver transforms (`transformations/bronze_to_silver/*_silver.py`) for all six entities
  - Gold marts (`transformations/silver_to_gold/*.py`) for six analytical products
- Shared modules
  - `core/config.py`: platform paths and catalog/storage configuration seams
  - `core/spark.py`: Spark session creation, table helpers, standardized writes, logging
- Data generation
  - `scripts/data_generator/generate_commerce_data.py`
- Storage
  - Raw files: `data/raw/*.csv`
  - Iceberg warehouse: `data/warehouse`
- Metadata contract
  - `metadata/datasets.yaml`

## End-to-End Pipeline (Module 1)

### Raw Layer (`data/raw`)

Operational commerce datasets:
- `customers.csv`
- `products.csv`
- `orders.csv`
- `order_items.csv`
- `payments.csv`
- `shipments.csv`

### Bronze Layer (`novalake.bronze`)

Raw datasets are loaded to Iceberg Bronze tables with technical metadata:
- `_ingestion_timestamp`
- `_source_file`

### Silver Layer (`novalake.silver`)

Entity-level cleansing and conformance:
- datatype normalization and naming consistency
- status/domain validation
- arithmetic validation for monetary fields
- referential integrity enforcement across entities

### Gold Layer (`novalake.gold`)

Business-facing analytical products:
- `daily_revenue`
- `sales_by_country`
- `top_products`
- `customer_revenue`
- `payment_success_rate`
- `shipment_delivery_summary`

## Gold Data Products and Purpose

- `daily_revenue`
  - Purpose: monitor daily revenue trend and order productivity.
- `sales_by_country`
  - Purpose: compare commercial performance across countries.
- `top_products`
  - Purpose: identify highest-performing products by revenue and units sold.
- `customer_revenue`
  - Purpose: understand customer-level revenue concentration and value profile.
- `payment_success_rate`
  - Purpose: track payment reliability by date and payment method.
- `shipment_delivery_summary`
  - Purpose: track shipment throughput, delay exposure, and delivery rate.

## Local Topology

- `spark-master` and `spark-worker` provide local distributed processing.
- `postgres` is included as operational-source anchor for future modules.
- Optional notebook service is isolated under compose `lab` profile.

## Module 1 as Baseline

Module 1 is the architecture baseline for all future modules. Later modules add capabilities (object storage, CDC, streaming, metadata intelligence, AI) while preserving this foundation's medallion contracts and shared runtime patterns.

## Evolution Direction

- Module 2: migrate warehouse backend to S3-compatible object storage.
- Module 3: introduce CDC ingestion from PostgreSQL.
- Module 4: add streaming analytics paths.
- Module 5: expand metadata intelligence and governance.
- Module 6: add AI-assisted platform workflows.
