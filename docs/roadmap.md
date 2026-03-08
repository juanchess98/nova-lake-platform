# NovaLake Architecture Roadmap

This roadmap defines how NovaLake evolves module by module while preserving continuity from the Module 1 foundation.

## Planning Principles

- Build one operational capability per module and keep previous modules stable.
- Preserve medallion semantics across all modules.
- Introduce new infrastructure only when the previous module value is already validated.
- Keep code structure and naming consistent as capabilities expand.

## Module Plan

### Module 1 - Lakehouse Foundation (Current)

### Scope

- Local Spark + Iceberg baseline
- Raw CSV ingestion to bronze
- Bronze to silver quality pipeline
- Silver to gold business aggregate (`daily_revenue`)
- Local warehouse storage (`data/warehouse`)

### Outcome

A deterministic, portfolio-grade local data platform that demonstrates clean lakehouse layering and reproducible execution.

### Module 2 - Storage Evolution

### Scope

- Evolve warehouse backing from local filesystem to S3-compatible object storage
- Externalize storage endpoint/bucket configuration
- Keep Spark job contracts and medallion naming unchanged

### Outcome

Storage becomes environment-portable while pipelines remain behaviorally consistent.

### Module 3 - CDC Ingestion

### Scope

- Introduce PostgreSQL change data capture ingestion
- Support incremental/near-real-time bronze updates
- Add ingestion observability for offsets/lag and failure visibility

### Outcome

NovaLake moves from batch snapshot ingestion toward operational-source continuity.

### Module 4 - Streaming Analytics

### Scope

- Introduce stream processing for selected entities and KPIs
- Blend micro-batch/streaming patterns with existing medallion layers
- Extend gold outputs to lower-latency analytical use cases

### Outcome

Platform supports both batch and streaming analytics patterns.

### Module 5 - Metadata Intelligence

### Scope

- Formalize dataset contracts and data quality expectations
- Add lineage/metadata enrichment and discoverability
- Standardize ownership and semantic definitions for critical datasets

### Outcome

Governance, trust, and discoverability become first-class platform capabilities.

### Module 6 - AI Copilot

### Scope

- Add AI-assisted platform operations and analytical assistance
- Enable guided diagnostics, data-product context, and workflow acceleration
- Keep human review and deterministic pipeline logic as controls

### Outcome

A practical AI layer that improves operator productivity without replacing engineering discipline.

## Cross-Module Continuity

- Bronze/silver/gold remains the core data contract.
- Shared utilities (`core/config.py`, `core/spark.py`) are the main evolution seam.
- ADRs in `docs/decisions.md` continue recording architecture choices at each step.
