# Architectural Decision Records

This file tracks key architecture decisions for NovaLake Platform.

## ADR-001: Adopt Apache Iceberg for Core Lakehouse Tables

- Status: Accepted
- Date: 2026-03-05

### Context

The platform requires a table format that can evolve with schema changes, support reliable upserts/reprocessing patterns, and remain engine-friendly for future modules.

### Decision

Use Apache Iceberg tables for all medallion layers in Module 1.

### Alternatives Considered

- Plain Parquet folders with manual metadata management
- Delta Lake
- Hive tables without modern table-format semantics

### Consequences

- Positive:
  - Schema and partition evolution support
  - ACID semantics for batch rewrites
  - Better long-term fit for modular platform growth
- Negative:
  - Requires explicit Spark Iceberg runtime configuration
  - Adds dependency management overhead in local development

### Follow-up

Evaluate catalog migration path (REST/Nessie/Glue) once multi-environment deployment is introduced.

## ADR-002: Use Local Hadoop Catalog for Module 1

- Status: Accepted
- Date: 2026-03-05

### Context

Module 1 prioritizes reproducibility and low setup friction over distributed catalog features.

### Decision

Use Iceberg Hadoop catalog with local warehouse path (`data/warehouse`).

### Alternatives Considered

- Hive Metastore-backed catalog
- REST catalog service
- Cloud-native catalog integrations

### Consequences

- Positive:
  - Minimal infrastructure footprint
  - Fast onboarding for portfolio reviewers
- Negative:
  - No centralized catalog service semantics
  - Not suitable as-is for team-scale deployments

### Follow-up

Introduce a service-backed catalog in a later module when deployment topology expands.

## ADR-003: Enforce Medallion Layering from Day One

- Status: Accepted
- Date: 2026-03-05

### Context

Early projects often collapse ingestion, cleansing, and business logic into a single layer, making evolution difficult.

### Decision

Use explicit namespaces for `bronze`, `silver`, and `gold` from the first module.

### Alternatives Considered

- Single-layer raw-to-mart pipeline
- Two-layer model (staging + marts)

### Consequences

- Positive:
  - Clear separation of concerns
  - Easier lineage and debugging
  - Cleaner path to contracts, orchestration, and observability
- Negative:
  - Slightly higher upfront structure and naming discipline

### Follow-up

Standardize per-layer quality gates and SLAs in future modules.

## ADR-004: Start with Batch CSV Ingestion for Foundational Module

- Status: Accepted
- Date: 2026-03-05

### Context

The first milestone is platform foundation, not full operational ingestion complexity.

### Decision

Start ingestion from local CSV datasets while including PostgreSQL service as near-term operational source.

### Alternatives Considered

- Direct Postgres incremental ingestion in Module 1
- Kafka/Debezium-first architecture

### Consequences

- Positive:
  - Controlled scope and faster architecture validation
  - Reliable deterministic test data
  - Clear progression path into CDC and streaming
- Negative:
  - Does not yet represent production ingestion latency characteristics

### Follow-up

Add Postgres incremental ingestion in Module 2, then CDC via Debezium in Module 3.
