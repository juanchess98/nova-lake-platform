# Module 3 - Catalog & Metadata Foundation

Module 3 keeps the Module 2 medallion pipeline and MinIO-backed storage intact while introducing Project Nessie as the dedicated Iceberg catalog.

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

## Catalog Configuration

NovaLake now uses environment-driven catalog settings in addition to storage settings:

- `NOVALAKE_CATALOG_BACKEND=nessie`
- `NOVALAKE_CATALOG_URI=http://nessie:19120/api/v1`
- `NOVALAKE_CATALOG_REF=main`
- `NOVALAKE_CATALOG_AUTH_TYPE=NONE`

Spark applies these settings through the shared helpers in `core/config.py`. Spark still uses the Iceberg Spark catalog wrapper, with `org.apache.iceberg.nessie.NessieCatalog` configured as the catalog implementation.

## Module 2 Compatibility

Module 2 assets remain in place:

- raw datasets still live in `data/raw`
- MinIO remains the storage layer for Iceberg table data
- ingestion and transformation scripts keep their existing interfaces
- table identifiers and namespaces remain unchanged

The primary behavior change is that Iceberg metadata is now managed through Nessie rather than the warehouse path alone.

## Local Execution

1. Copy `.env.example` to `.env`.
2. Start the stack with `.\scripts\run_job.ps1 up` or `./scripts/run_job.sh up`.
3. Validate Nessie at `http://localhost:19120/api/v1/config`.
4. Run the medallion pipeline with `bronze`, `silver`, and `gold` or `all`.
5. Validate with `SHOW NAMESPACES IN novalake`.
6. Inspect the MinIO console at `http://localhost:9001`.
