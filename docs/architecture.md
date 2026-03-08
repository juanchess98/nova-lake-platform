# Architecture - Module 1 (Lakehouse Foundation)

## Purpose

Establish a local, reproducible lakehouse baseline with engineering conventions that can evolve cleanly into later NovaLake modules.

## Design Principles

- Local-first execution and deterministic sample data
- Explicit medallion separation (`bronze`, `silver`, `gold`)
- Shared runtime utilities instead of job-level hardcoding
- Simple operational patterns with clear execution logs
- Evolution-ready configuration seams without premature infrastructure complexity

## Module 1 Runtime Components

- Spark jobs
  - `ingestion/batch/load_orders_to_bronze.py`
  - `transformations/bronze_to_silver/orders_silver.py`
  - `transformations/silver_to_gold/daily_revenue.py`
- Shared modules
  - `core/config.py`: paths, storage backend selection seam, catalog config
  - `core/spark.py`: Spark session factory, namespace/table helpers, standardized writes, lightweight logging setup
- Storage
  - Raw files: `data/raw/*.csv`
  - Iceberg warehouse: `data/warehouse`
- Metadata contract
  - `metadata/datasets.yaml`
- Optional exploration
  - `notebooks/` via compose `lab` profile

## Logical Data Layers

- Bronze (`novalake.bronze`)
  - ingestion-aligned representation
  - technical lineage fields (`_ingestion_timestamp`, `_source_file`)
- Silver (`novalake.silver`)
  - standardized datatypes and naming
  - quality filtering and deterministic deduplication
- Gold (`novalake.gold`)
  - business-facing aggregate outputs
  - current artifact: `daily_revenue`

## Local Topology

- `postgres`: operational source prepared for upcoming ingestion evolution
- `spark-master` and `spark-worker`: local distributed Spark runtime
- Spark jobs submit to `spark://spark-master:7077`

## Current Data Flow

1. Ingest `orders.csv` into `novalake.bronze.orders`.
2. Standardize and validate into `novalake.silver.orders`.
3. Aggregate into `novalake.gold.daily_revenue`.

## Versioned Diagram (Module 1)

- Diagram file: `docs/diagrams/module1-v1.mmd`

```mermaid
flowchart LR
    subgraph Sources[Data Sources]
        RAW[Raw CSV Files\n(data/raw/*.csv)]
        PG[(PostgreSQL\nOperational Source)]
    end

    subgraph Runtime[Spark Runtime]
        JOB1[Ingestion Job\nload_orders_to_bronze.py]
        JOB2[Transform Job\norders_silver.py]
        JOB3[Transform Job\ndaily_revenue.py]
    end

    subgraph Catalog[Iceberg Catalog: novalake]
        B[(bronze.orders)]
        S[(silver.orders)]
        G[(gold.daily_revenue)]
    end

    subgraph Storage[Local Warehouse Storage]
        W[(data/warehouse)]
    end

    LAB[Optional Notebook Environment\n(JupyterLab)]

    RAW --> JOB1 --> B
    B --> JOB2 --> S
    S --> JOB3 --> G

    B --> W
    S --> W
    G --> W

    PG -. prepared source for later modules .-> JOB1
    LAB -. exploration and validation .-> B
    LAB -. exploration and validation .-> S
    LAB -. exploration and validation .-> G
```

## Architecture Evolution (Module-to-Module)

- Module 1: local lakehouse foundation with deterministic batch flow.
- Module 2: storage evolution to S3-compatible object storage without changing medallion contracts.
- Module 3: CDC ingestion from PostgreSQL into bronze.
- Module 4: streaming analytics on top of established medallion patterns.
- Module 5: metadata intelligence, lineage, and contract maturity.
- Module 6: AI copilot capabilities for platform operations and analytical acceleration.

Formal roadmap: see `docs/roadmap.md`.

## Storage Model Comparison

### Module 1 (Current): Local Filesystem Warehouse

- Warehouse path is local (`data/warehouse`) and managed by the Iceberg Hadoop catalog.
- Best for reproducibility, low setup cost, and straightforward portfolio demos.
- Trade-off: not suitable for distributed/shared environments.

### Module 2 (Planned): S3-Compatible Object Storage

- Warehouse location moves to object storage URI with endpoint/bucket credentials.
- Better fit for environment portability and multi-runtime access.
- Trade-off: higher operational complexity (credentials, endpoints, bucket policies, networking).

### Why Module 1 Stays Simpler

Module 1 intentionally optimizes for architectural clarity and deterministic local operation. This keeps focus on core lakehouse contracts first, then introduces storage complexity in Module 2 once baseline behavior is already validated.

## Extension Hooks

- `core/config.py` isolates storage/catalog wiring to minimize future migration changes.
- `core/spark.py` centralizes Spark and table write behavior for naming and operational consistency.
- ADR workflow (`docs/decisions.md`) preserves architecture rationale as module scope expands.
- Stabilization learnings are tracked in `docs/stabilization.md`.
