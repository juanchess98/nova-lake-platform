# NovaLake Platform

NovaLake is a modular lakehouse platform that demonstrates how a modern data platform evolves module by module.

**Current baseline:** Module 2 - Storage Evolution.

## Module 2 Deliverables

Module 2 keeps the Module 1 lakehouse flow intact while moving Iceberg table storage to MinIO-backed object storage:
- synthetic commerce data generator (`scripts/data_generator/generate_commerce_data.py`)
- six raw datasets (`customers`, `products`, `orders`, `order_items`, `payments`, `shipments`)
- raw -> bronze -> silver -> gold batch pipeline on Spark + Iceberg
- Iceberg warehouse rooted in MinIO via S3A
- compute/storage separation between Spark runtime and object storage
- six gold analytical data products:
  - `daily_revenue`
  - `sales_by_country`
  - `top_products`
  - `customer_revenue`
  - `payment_success_rate`
  - `shipment_delivery_summary`

MinIO is now part of the local platform runtime. Kafka, Debezium, and dbt remain out of scope.

## Architecture Story

NovaLake follows a medallion contract: raw -> bronze -> silver -> gold.

- Raw: reproducible CSV operational data
- Bronze: ingestion-aligned Iceberg tables with technical lineage metadata
- Silver: standardized and validated domain-conformed datasets
- Gold: business-facing analytical data products
- Storage: MinIO object storage for Iceberg table data and metadata

## Documentation Map

- Architecture index: `docs/architecture.md`
- Module 1 formal architecture: `docs/architecture/module_01_lakehouse_foundation.md`
- Module 2 formal architecture: `docs/architecture/module_02_storage_evolution.md`
- Use case: `docs/use_case.md`
- Domain model: `docs/domain_model.md`
- Requirements: `docs/requirements.md`
- Roadmap: `docs/roadmap.md`
- Architectural decisions (ADRs): `docs/decisions.md`
- Stabilization notes: `docs/stabilization.md`
- Metadata contract: `metadata/datasets.yaml`
- Rendered diagrams: `docs/diagrams/module-1.png`, `docs/diagrams/module-2 Storage Evolution.png`
- Diagram sources: `docs/diagrams/module1-v1.mmd`, `docs/diagrams/module2-storage-evolution-stub.mmd`

## Run Locally

### Prerequisite: required environment file

Module 2 scripts require a project-root `.env` file. Create it before running any `run_*`, `sql_shell`, or `lab_health` script.

PowerShell:
```powershell
Copy-Item .env.example .env
```

Bash:
```bash
cp .env.example .env
```

### Start services

PowerShell:
```powershell
.\scripts\run_job.ps1 up
```

Bash:
```bash
./scripts/run_job.sh up
```

This starts PostgreSQL, Spark, and MinIO. MinIO API is exposed at `http://localhost:9000` and the console at `http://localhost:9001`.

### Run full Module 2 pipeline

PowerShell:
```powershell
.\scripts\run_job.ps1 all
```

Bash:
```bash
./scripts/run_job.sh all
```

### Validate storage and gold outputs

Check that the medallion namespaces exist through Spark SQL:

PowerShell:
```powershell
.\scripts\sql_shell.ps1 -Query "SHOW NAMESPACES IN novalake"
```

Bash:
```bash
./scripts/sql_shell.sh -q "SHOW NAMESPACES IN novalake"
```

Then validate a gold table:

PowerShell:
```powershell
.\scripts\sql_shell.ps1 -Query "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date"
```

Bash:
```bash
./scripts/sql_shell.sh -q "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date"
```

### Optional notebook lab

PowerShell:
```powershell
.\scripts\run_lab.ps1 up
```

Bash:
```bash
./scripts/run_lab.sh up
```

Open `http://localhost:8888` and use kernel **PySpark (NovaLake)**.

### Local validation steps

1. Copy `.env.example` to `.env`.
2. Start services with `.\scripts\run_job.ps1 up` or `./scripts/run_job.sh up`.
3. Run the full pipeline with `.\scripts\run_job.ps1 all` or `./scripts/run_job.sh all`.
4. Confirm catalog visibility with `SHOW NAMESPACES IN novalake`.
5. Open the MinIO console at `http://localhost:9001` and verify bucket `novalake-lakehouse` contains the `warehouse/` prefix with `bronze/`, `silver/`, and `gold/` table data.
6. Optionally start JupyterLab with `.\scripts\run_lab.ps1 up` or `./scripts/run_lab.sh up` and query the same tables interactively.

## Module Evolution

- Module 1: Lakehouse Foundation
- Module 2: Storage Evolution (current baseline)
- Module 3: CDC Ingestion
- Module 4: Streaming Analytics
- Module 5: Metadata Intelligence
- Module 6: AI Copilot
