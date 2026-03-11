# NovaLake Platform

NovaLake is a modular lakehouse platform that demonstrates how a modern data platform evolves module by module.

**Current baseline:** Module 1 - Lakehouse Foundation.

## Module 1 Deliverables

Module 1 is fully implemented and operational with:
- synthetic commerce data generator (`scripts/data_generator/generate_commerce_data.py`)
- six raw datasets (`customers`, `products`, `orders`, `order_items`, `payments`, `shipments`)
- raw -> bronze -> silver -> gold batch pipeline on Spark + Iceberg
- six gold analytical data products:
  - `daily_revenue`
  - `sales_by_country`
  - `top_products`
  - `customer_revenue`
  - `payment_success_rate`
  - `shipment_delivery_summary`

Module 1 intentionally does not include MinIO, Kafka, Debezium, or dbt yet.

## Architecture Story

NovaLake follows a medallion contract: raw -> bronze -> silver -> gold.

- Raw: reproducible CSV operational data
- Bronze: ingestion-aligned Iceberg tables with technical lineage metadata
- Silver: standardized and validated domain-conformed datasets
- Gold: business-facing analytical data products

## Documentation Map

- Architecture index: `docs/architecture.md`
- Module 1 formal architecture: `docs/architecture/module_01_lakehouse_foundation.md`
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

Module 1 scripts now require a project-root `.env` file. Create it before running any `run_*`, `sql_shell`, or `lab_health` script.

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

### Run full Module 1 pipeline

PowerShell:
```powershell
.\scripts\run_job.ps1 all
```

Bash:
```bash
./scripts/run_job.sh all
```

### Validate gold outputs

PowerShell:
```powershell
.\scripts\sql_shell.ps1 -Query "SHOW TABLES IN novalake.gold"
```

Bash:
```bash
./scripts/sql_shell.sh -q "SHOW TABLES IN novalake.gold"
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

## Module Evolution

- Module 1: Lakehouse Foundation (current baseline)
- Module 2: Storage Evolution (S3-compatible object storage)
- Module 3: CDC Ingestion
- Module 4: Streaming Analytics
- Module 5: Metadata Intelligence
- Module 6: AI Copilot
