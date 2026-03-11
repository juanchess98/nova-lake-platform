# NovaLake Architecture Roadmap

This roadmap defines how NovaLake evolves module by module while preserving continuity from the Module 1 baseline.

## Planning Principles

- Deliver one major capability focus per module while keeping previous modules stable.
- Preserve medallion contracts (`bronze`, `silver`, `gold`) across modules.
- Introduce new infrastructure only when prior module value is validated.
- Keep shared interfaces and naming conventions consistent as scope expands.

## Module Plan

### Module 1 - Lakehouse Foundation (Current Baseline)

#### Scope

- local Spark + Iceberg architecture
- deterministic synthetic commerce data generator
- six raw operational datasets (`customers`, `products`, `orders`, `order_items`, `payments`, `shipments`)
- full raw -> bronze -> silver -> gold batch flow
- six gold analytical products:
  - `daily_revenue`
  - `sales_by_country`
  - `top_products`
  - `customer_revenue`
  - `payment_success_rate`
  - `shipment_delivery_summary`
- local warehouse storage (`data/warehouse`)

#### Outcome

A portfolio-grade, reproducible local baseline with clear data contracts and modular evolution seams.

### Module 2 - Storage Evolution

![Module 2 storage evolution diagram showing the transition from local warehouse-backed storage to S3-compatible object storage while preserving the medallion flow.](./diagrams/module-2%20Storage%20Evolution.png)

Rendered concept diagram for the planned storage evolution. Source: `docs/diagrams/module2-storage-evolution-stub.mmd`.

#### Scope

- evolve warehouse backing from local filesystem to S3-compatible object storage
- externalize storage endpoint/bucket configuration
- keep Spark job contracts and medallion naming unchanged

#### Outcome

Storage becomes environment-portable while pipelines remain behaviorally consistent.

### Module 3 - CDC Ingestion

#### Scope

- introduce PostgreSQL change data capture ingestion
- support incremental/near-real-time bronze updates
- add ingestion observability for offsets/lag and failure visibility

#### Outcome

NovaLake moves from batch snapshot ingestion toward operational-source continuity.

### Module 4 - Streaming Analytics

#### Scope

- introduce stream processing for selected entities and KPIs
- blend micro-batch/streaming patterns with existing medallion layers
- extend gold outputs to lower-latency analytical use cases

#### Outcome

Platform supports both batch and streaming analytics patterns.

### Module 5 - Metadata Intelligence

#### Scope

- formalize dataset contracts and data quality expectations
- add lineage/metadata enrichment and discoverability
- standardize ownership and semantic definitions for critical datasets

#### Outcome

Governance, trust, and discoverability become first-class platform capabilities.

### Module 6 - AI Copilot

#### Scope

- add AI-assisted platform operations and analytical assistance
- enable guided diagnostics, data-product context, and workflow acceleration
- keep human review and deterministic pipeline logic as controls

#### Outcome

A practical AI layer that improves operator productivity without replacing engineering discipline.

## Cross-Module Continuity

- Medallion layering remains the core data contract.
- Shared utilities (`core/config.py`, `core/spark.py`) are the main evolution seam.
- ADRs in `docs/decisions.md` continue recording architecture decisions at each stage.
