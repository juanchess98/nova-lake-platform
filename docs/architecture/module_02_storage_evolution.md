# Module 2 - Storage Evolution

Module 2 keeps the Module 1 medallion pipeline and Spark job structure intact while moving Iceberg table storage from the local warehouse path to MinIO-backed object storage.

## Architecture Intent

- keep raw CSV generation and ingestion local to the repo
- separate compute from storage by moving Iceberg table data into object storage
- preserve catalog naming and medallion namespaces:
  - `novalake.bronze.*`
  - `novalake.silver.*`
  - `novalake.gold.*`

## Runtime Topology

Components:
- synthetic data generator writes CSV files into `data/raw`
- Spark jobs run in the NovaLake Spark runtime containers
- Iceberg tables are stored under `s3a://novalake-lakehouse/warehouse`
- MinIO provides the S3-compatible API and object persistence
- JupyterLab remains an optional exploration surface

## Storage Configuration

NovaLake now uses environment-driven storage settings:

- `NOVALAKE_STORAGE_BACKEND=s3_compatible`
- `NOVALAKE_S3_ENDPOINT=http://minio:9000`
- `NOVALAKE_S3_ACCESS_KEY`
- `NOVALAKE_S3_SECRET_KEY`
- `NOVALAKE_S3_BUCKET=novalake-lakehouse`
- `NOVALAKE_S3_WAREHOUSE_PREFIX=warehouse`
- `NOVALAKE_S3_PATH_STYLE_ACCESS=true`

Spark applies these settings through the shared helpers in `core/config.py`.

## Module 1 Compatibility

Module 1 assets remain in place:

- raw datasets still live in `data/raw`
- the local warehouse directory remains available as a fallback backend
- ingestion and transformation scripts keep their existing interfaces

The primary behavior change is the Iceberg warehouse target.

## Local Execution

1. Copy `.env.example` to `.env`.
2. Start the stack with `.\scripts\run_job.ps1 up` or `./scripts/run_job.sh up`.
3. Run the full medallion pipeline with `all`.
4. Validate tables with Spark SQL or notebooks.
5. Inspect the MinIO console at `http://localhost:9001`.
