# NovaLake Platform

NovaLake is a modular lakehouse platform that demonstrates how a modern data platform evolves module by module.

**Current baseline:** Module 1 - Lakehouse Foundation.

## Module 1 Baseline

Module 1 establishes a local-first, production-style baseline with deterministic synthetic commerce data and end-to-end batch pipelines.

Implemented in Module 1:
- Synthetic commerce data generator (`scripts/data_generator/generate_commerce_data.py`)
- Six operational raw datasets (`customers`, `products`, `orders`, `order_items`, `payments`, `shipments`)
- Bronze ingestion jobs for all six datasets
- Silver cleaning/validation jobs with referential integrity checks
- Gold analytical data products for core business monitoring
- Spark + Iceberg medallion architecture in a containerized local environment

Module 1 intentionally does not include MinIO, Kafka, Debezium, or dbt yet.

## Architecture Story

NovaLake follows raw -> bronze -> silver -> gold:

1. Raw: reproducible CSV operational snapshots generated locally
2. Bronze: ingestion-aligned Iceberg tables with ingestion metadata
3. Silver: standardized, validated, referentially consistent domain tables
4. Gold: business-facing aggregates and monitoring datasets

Core architecture docs:
- `docs/architecture.md`
- `docs/domain_model.md`
- `docs/use_case.md`
- `docs/roadmap.md`
- `docs/decisions.md`

## Module 1 Data Scope

Raw entities:
- `customers`
- `products`
- `orders`
- `order_items`
- `payments`
- `shipments`

Gold analytical datasets:
- `daily_revenue`: daily commercial performance trend
- `sales_by_country`: country-level revenue and order behavior
- `top_products`: top product ranking by revenue and units sold
- `customer_revenue`: customer lifetime revenue and order profile
- `payment_success_rate`: payment execution health by method/date
- `shipment_delivery_summary`: fulfillment and delivery performance

## Run Locally

### 1. Start services

PowerShell:
```powershell
.\scripts\run_job.ps1 up
```

Bash:
```bash
./scripts/run_job.sh up
```

### 2. Run full Module 1 pipeline

PowerShell:
```powershell
.\scripts\run_job.ps1 all
```

Bash:
```bash
./scripts/run_job.sh all
```

### 3. Validate gold outputs

PowerShell:
```powershell
.\scripts\sql_shell.ps1 -Query "SHOW TABLES IN novalake.gold"
```

Bash:
```bash
./scripts/sql_shell.sh -q "SHOW TABLES IN novalake.gold"
```

### 4. Optional notebook lab

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

The design goal is stable contracts and controlled capability growth across modules.
