# Module 01 - Lakehouse Foundation

## Purpose

Establish NovaLake's formal architecture baseline as a local-first, reproducible lakehouse with end-to-end commerce analytics.

## Scope

Module 1 includes:
- synthetic commerce data generation
- six operational raw datasets
- full raw -> bronze -> silver -> gold batch flow
- six Gold analytical products
- local Spark + Iceberg deployment in containers

Out of scope for Module 1:
- object storage migration
- CDC and streaming ingestion
- external orchestration and metadata services

## Architectural Principles

- local-first reproducibility
- explicit medallion boundaries
- shared Spark/config utilities for consistency
- validated Silver contracts before Gold aggregation
- deliberate simplicity with future evolution seams

## Runtime Components

- Data generator
  - `scripts/data_generator/generate_commerce_data.py`
- Ingestion jobs (Bronze)
  - `ingestion/batch/load_*_to_bronze.py` for all six entities
- Transformation jobs (Silver)
  - `transformations/bronze_to_silver/*_silver.py`
- Analytical jobs (Gold)
  - `transformations/silver_to_gold/*.py`
- Shared runtime
  - `core/config.py`
  - `core/spark.py`
- Storage
  - Raw CSV: `data/raw/`
  - Iceberg warehouse: `data/warehouse`
- Metadata contract
  - `metadata/datasets.yaml`

## Data Flow

1. Generate deterministic synthetic operational commerce datasets.
2. Ingest raw CSV datasets into `novalake.bronze.*` Iceberg tables.
3. Clean and validate into `novalake.silver.*` entity tables.
4. Build business-facing `novalake.gold.*` analytical products.

## Medallion Layers

### Raw

Source files:
- `customers.csv`
- `products.csv`
- `orders.csv`
- `order_items.csv`
- `payments.csv`
- `shipments.csv`

### Bronze (`novalake.bronze`)

Ingestion-aligned representation with technical lineage metadata:
- `_ingestion_timestamp`
- `_source_file`

### Silver (`novalake.silver`)

Conformed operational entities with:
- type and naming normalization
- domain/status validation
- monetary consistency checks
- referential integrity enforcement

### Gold (`novalake.gold`)

Curated analytical products:
- `daily_revenue`
- `sales_by_country`
- `top_products`
- `customer_revenue`
- `payment_success_rate`
- `shipment_delivery_summary`

## Domain Model Summary

Core entities and relationships:
- customer -> orders (1:N)
- orders -> order_items (1:N)
- products -> order_items (1:N)
- orders -> payments (1:N)
- orders -> shipments (0..1 in Module 1 simulation)

Reference: `docs/domain_model.md`.

## Gold Analytical Products

- `daily_revenue`
  - daily revenue trend and order productivity
- `sales_by_country`
  - country-level sales comparison
- `top_products`
  - product ranking by revenue and units sold
- `customer_revenue`
  - customer-level revenue concentration
- `payment_success_rate`
  - payment reliability by method/date
- `shipment_delivery_summary`
  - shipment status and delivery performance

## Local Deployment Topology

- `spark-master` + `spark-worker` for distributed local compute
- `postgres` included as operational-source anchor for future ingestion evolution
- optional `notebook-lab` profile for exploration
- project-root `.env` file is required for compose/script credential resolution (`.env.example` is the template)

## Current Limitations

- local filesystem warehouse only (`data/warehouse`)
- batch-centric ingestion and transformations
- single-environment local deployment
- no CDC/streaming or centralized metadata service yet

## Evolution Path to Module 2

Module 2 preserves this architecture and migrates storage from local warehouse to S3-compatible object storage while keeping medallion contracts and Spark job interfaces stable.
