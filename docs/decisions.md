# Architectural Decision Records

This file tracks key architecture decisions for NovaLake Platform.

References:
- architecture index: `docs/architecture.md`
- Module 1 formal architecture: `docs/architecture/module_01_lakehouse_foundation.md`
- stabilization notes: `docs/stabilization.md`

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

Add object storage in Module 2, then CDC via Debezium in Module 3.

## ADR-005: Pre-Bundle Iceberg Runtime in Custom Spark Image

- Status: Accepted
- Date: 2026-03-06

### Context

Using `spark-submit --packages ...` at runtime introduces dependency on external Maven availability and creates environment-specific failures.

### Decision

Build a custom Spark image (`infra/spark/Dockerfile`) that includes the Iceberg runtime JAR ahead of time.

### Alternatives Considered

- Runtime package resolution with `--packages`
- Manual per-container JAR provisioning

### Consequences

- Positive:
  - More deterministic local runs
  - Less command complexity for users
  - Lower chance of transient dependency-resolution failures
- Negative:
  - Adds a build step when updating Spark/Iceberg versions

### Follow-up

Add image-tagging strategy per module/environment when CI/CD is introduced.

## ADR-006: Add Notebook UX as Optional Lab Profile

- Status: Accepted
- Date: 2026-03-06

### Context

Developers and reviewers need a faster way to explore data and validate outputs without repeating long CLI commands. At the same time, transformation logic must remain production-like and versioned in Python modules.

### Decision

Add an optional JupyterLab service in Docker Compose under profile `lab`, keeping notebooks in `notebooks/` as exploratory interfaces only.

### Alternatives Considered

- No notebook interface (CLI only)
- Notebook-first pipeline implementation

### Consequences

- Positive:
  - Better DX for ad-hoc analysis and demos
  - Stronger portfolio storytelling
  - Preserves production code discipline in `ingestion/` and `transformations/`
- Negative:
  - Additional image/service to maintain
  - Requires explicit guidance to avoid business logic drift into notebooks

### Follow-up

Introduce notebook quality conventions (naming, output clearing, promotion rules) when notebook count grows.

## ADR-007: Move Iceberg Warehouse Storage to S3-Compatible Object Storage

- Status: Accepted
- Date: 2026-03-14

### Context

The local Hadoop catalog from Module 1 is sufficient for a single-host baseline, but it keeps compute and storage coupled to the project filesystem. Module 2 requires object storage semantics while preserving existing Spark job contracts and medallion naming.

### Decision

Keep the Iceberg Hadoop catalog, but move the warehouse root to MinIO through the S3A filesystem (`s3a://novalake-lakehouse/warehouse`) and externalize the endpoint, credentials, bucket, and path-style access configuration through environment variables.

### Alternatives Considered

- Keep the local filesystem warehouse and only add MinIO for raw files
- Introduce a REST or Hive-backed Iceberg catalog in Module 2
- Use runtime `--packages` resolution instead of pre-bundled S3 dependencies

### Consequences

- Positive:
  - Clear compute/storage separation in local development
  - Storage configuration becomes portable across S3-compatible environments
  - Existing ingestion and transformation entrypoints remain stable
- Negative:
  - Requires additional local infrastructure and S3A dependency management
  - Catalog metadata is still file-backed rather than service-backed

### Follow-up

Adopt a service-backed Iceberg catalog in the next platform module once metadata becomes a dedicated architectural concern.

## ADR-008: Introduce Project Nessie as the Dedicated Iceberg Catalog

- Status: Accepted
- Date: 2026-03-17

### Context

Module 2 separated compute from storage by moving Iceberg data into MinIO, but the catalog remained Hadoop-based and still coupled to the warehouse path. Module 3 requires a dedicated metadata layer without changing existing job contracts or physical storage.

### Decision

Use Project Nessie as the Iceberg catalog backend for NovaLake while keeping MinIO as the object store and Spark as the processing engine.

### Alternatives Considered

- Keep the Hadoop catalog in place
- Introduce Hive Metastore
- Introduce a generic Iceberg REST catalog

### Consequences

- Positive:
  - Catalog metadata is now service-backed and decoupled from storage
  - Existing medallion namespaces and table identifiers stay stable
  - The platform gains a clear metadata-layer evolution seam for future modules
- Negative:
  - Adds a new service to the local stack
  - Requires Nessie runtime dependencies in the Spark image
  - Local Module 3 development intentionally runs Nessie with an in-memory version store, so catalog state is not treated as durable across every container lifecycle scenario

### Follow-up

Use the Nessie-backed metadata layer as the foundation for CDC orchestration, metadata-driven pipelines, and metadata intelligence in later modules.

## ADR-009: Centralize Module 3 Spark Catalog Configuration in Shared Helpers

- Status: Accepted
- Date: 2026-04-13

### Context

Module 3 introduced multiple Spark execution surfaces: batch jobs, `spark-sql` helpers, and the optional notebook lab. The core catalog wiring already lived in `core/config.py`, but the notebook runtime still duplicated Iceberg, Nessie, and S3A configuration in Docker Compose. At the same time, `spark.sql.catalogImplementation=in-memory` was still being applied broadly even though Nessie had become the real catalog backend.

### Decision

Make `core/config.py` the shared source of truth for Module 3 Spark catalog settings. Remove `spark.sql.catalogImplementation=in-memory` from the general Spark runtime config, but keep it in the `spark-sql` wrappers only as a local CLI safeguard against the embedded Hive metastore and Derby lock contention.

### Alternatives Considered

- Keep duplicating catalog settings in Docker Compose and shell wrappers
- Remove `spark.sql.catalogImplementation=in-memory` everywhere, including `spark-sql`
- Move all Spark configuration fully into Compose environment variables

### Consequences

- Positive:
  - Runtime configuration now matches the Module 3 architecture more accurately
  - Notebook, jobs, and helper scripts are less likely to drift apart
  - The reason for the remaining `spark-sql` override is explicit and reviewable
- Negative:
  - Wrapper scripts now depend on the shared Python config helper for startup
  - The local `spark-sql` path still carries a CLI-specific compatibility rule that future modules should revisit if the interactive surface changes

### Follow-up

Reassess the CLI-specific Hive suppression rule if NovaLake later standardizes on a different interactive SQL entrypoint or adds stronger automated environment validation.
