# Module 3 - Catalog & Metadata Foundation

Module 3 keeps the Module 2 medallion pipeline and MinIO-backed storage intact while introducing Project Nessie as the dedicated Iceberg catalog. This hardening pass keeps that architecture unchanged while making the baseline more explicit and easier to validate before Module 4.

## Architecture Intent

- separate the metadata layer from the physical warehouse location
- keep Spark as the compute engine and MinIO as the object storage backend
- preserve catalog naming and medallion namespaces:
  - `novalake.bronze.*`
  - `novalake.silver.*`
  - `novalake.gold.*`

## Runtime Topology

Components:
- synthetic data generator writes CSV files into `data/raw`
- Spark jobs run in the NovaLake Spark runtime containers
- MinIO stores Iceberg table data under `s3a://novalake-lakehouse/warehouse`
- Nessie serves the Iceberg catalog API at `http://nessie:19120/api/v1`
- JupyterLab remains an optional exploration surface

Local-development tradeoff:
- the local Nessie service runs with `nessie.version.store.type=IN_MEMORY`
- this is intentional for Module 3 because it keeps local startup simple and reproducible
- catalog state should be treated as development-oriented rather than durable across every lifecycle event

## Catalog Configuration

NovaLake now uses environment-driven catalog settings in addition to storage settings:

- `NOVALAKE_CATALOG_BACKEND=nessie`
- `NOVALAKE_CATALOG_URI=http://nessie:19120/api/v1`
- `NOVALAKE_CATALOG_REF=main`
- `NOVALAKE_CATALOG_AUTH_TYPE=NONE`

Spark applies these settings through the shared helpers in `core/config.py`. Spark still uses the Iceberg Spark catalog wrapper, with `org.apache.iceberg.nessie.NessieCatalog` configured as the catalog implementation.

Hardening-pass clarification:
- shared Spark runtime config no longer declares `spark.sql.catalogImplementation=in-memory`
- Nessie is the real catalog layer for Spark jobs and notebook sessions
- the `spark-sql` helper wrappers still add `spark.sql.catalogImplementation=in-memory` as a CLI-only safeguard so local interactive SQL does not contend with Spark's embedded Hive metastore

## Module 2 Compatibility

Module 2 assets remain in place:

- raw datasets still live in `data/raw`
- MinIO remains the storage layer for Iceberg table data
- ingestion and transformation scripts keep their existing interfaces
- table identifiers and namespaces remain unchanged

The primary behavior change is that Iceberg metadata is now managed through Nessie rather than the warehouse path alone.

What remained unchanged from Module 2:

- MinIO is still the physical storage backend
- Spark jobs keep the same entrypoints and medallion responsibilities
- Bronze, Silver, and Gold table names remain stable

What this hardening pass improved:

- reduced Spark configuration drift by making the notebook lab derive catalog settings from `core/config.py`
- made the local Nessie in-memory mode explicit
- strengthened operational validation with namespace and representative Gold-query checks
- clarified the Module 3 handoff baseline for upcoming CDC work

## Local Execution

1. Copy `.env.example` to `.env`.
2. Start the stack with `.\scripts\run_job.ps1 up` or `./scripts/run_job.sh up`.
3. Validate Nessie at `http://localhost:19120/api/v1/config`.
4. Run the medallion pipeline with `bronze`, `silver`, and `gold` or `all`.
5. Validate with `SHOW NAMESPACES IN novalake`.
6. Validate with `SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date`.
7. Run `.\scripts\lab_health.ps1` or `./scripts/lab_health.sh` if the optional notebook profile is running.
8. Inspect the MinIO console at `http://localhost:9001`.
