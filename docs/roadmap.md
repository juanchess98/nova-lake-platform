# NovaLake Architecture Roadmap

This roadmap defines how NovaLake evolves module by module while preserving continuity from the current Module 3 baseline.

## Planning Principles

- Deliver one major capability focus per module while keeping previous modules stable.
- Preserve medallion contracts (`bronze`, `silver`, `gold`) across modules.
- Introduce new infrastructure only when prior module value is validated.
- Keep shared interfaces, namespaces, and table names consistent as scope expands.

## Module Plan

### Module 1 - Lakehouse Foundation

#### Scope

- local Spark + Iceberg architecture
- deterministic synthetic commerce data generator
- six raw operational datasets (`customers`, `products`, `orders`, `order_items`, `payments`, `shipments`)
- full raw -> bronze -> silver -> gold batch flow
- local warehouse storage (`data/warehouse`)

#### Outcome

A reproducible local lakehouse baseline with explicit medallion layering.

### Module 2 - Storage Evolution

#### Scope

- move Iceberg table storage from local filesystem to MinIO-backed object storage
- externalize S3-compatible endpoint, bucket, and credential configuration
- keep Spark job contracts and medallion naming unchanged

#### Outcome

Compute and storage become decoupled while pipelines remain behaviorally consistent.

### Module 3 - Catalog & Metadata Foundation

#### Scope

- introduce Project Nessie as the dedicated Iceberg catalog
- decouple metadata management from the physical warehouse path
- keep MinIO as the storage backend and Spark as the compute engine
- preserve existing `novalake.bronze`, `novalake.silver`, and `novalake.gold` contracts

#### Outcome

NovaLake gains a dedicated metadata layer that aligns the platform with modern lakehouse architecture.

Status: current baseline

### Module 4 - CDC Ingestion

#### Scope

- introduce PostgreSQL change data capture ingestion
- support incremental bronze updates from operational systems
- add ingestion observability for offsets, lag, and failures

#### Outcome

NovaLake moves from batch snapshot ingestion toward operational-source continuity.

### Module 5 - Streaming Analytics

#### Scope

- introduce stream and micro-batch processing for selected entities and KPIs
- extend existing medallion layers to lower-latency use cases
- support near-real-time analytical data products

#### Outcome

Platform supports both batch and streaming analytics patterns.

### Module 6 - Metadata-Driven Pipelines

#### Scope

- drive ingestion and transformation behavior from metadata
- reduce hardcoded table orchestration and configuration drift
- improve maintainability as dataset count grows

#### Outcome

Pipeline behavior becomes more dynamic and easier to scale.

### Module 7 - Metadata Intelligence

#### Scope

- formalize data contracts and quality expectations
- add lineage, ownership, and discoverability metadata
- raise governance and trust as first-class platform capabilities

#### Outcome

Metadata evolves from configuration into an active control plane.

### Module 8 - AI Copilot

#### Scope

- add AI-assisted platform operations and analytical guidance
- enable guided diagnostics, metadata-aware exploration, and developer acceleration
- keep human review and deterministic pipeline logic as controls

#### Outcome

A practical AI layer improves platform productivity without displacing engineering discipline.

## Cross-Module Continuity

- Medallion layering remains the core data contract.
- Object storage remains the physical table storage layer after Module 2.
- Shared utilities (`core/config.py`, `core/spark.py`) remain the main evolution seam.
- ADRs in `docs/decisions.md` continue recording architecture decisions at each stage.
