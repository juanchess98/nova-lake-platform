# NovaLake Platform

NovaLake Platform is a portfolio-grade local data platform built to evolve in modules. The current release is **Module 1: Lakehouse Foundation**.

## Architecture-First Positioning

Module 1 is intentionally local-first and focused on strong foundations:

- Apache Spark + Apache Iceberg medallion layers (`bronze`, `silver`, `gold`)
- Shared Python core utilities for configuration and Spark behavior consistency
- Deterministic batch ingestion from raw CSV data
- Operational-quality conventions (clean job boundaries, lightweight execution logging, ADRs)
- PostgreSQL included as the operational source anchor for future ingestion modules

Module 1 intentionally does **not** add MinIO, Kafka, Debezium, or dbt yet.

## Module 1 Scope

- Dockerized local runtime
- Spark processing with Iceberg tables
- Batch flow: `orders` raw -> bronze -> silver -> gold
- Local warehouse storage at `data/warehouse`
- Optional notebook environment for exploration

## Architecture Artifacts

- Architecture overview: `docs/architecture.md`
- Module roadmap (Modules 1-6): `docs/roadmap.md`
- Architecture decisions (ADRs): `docs/decisions.md`
- Stabilization history: `docs/stabilization.md`
- Versioned Module 1 diagram: `docs/diagrams/module1-v1.mmd`

## Repository Layout

```text
nova-lake-platform/
|-- core/
|   |-- config.py
|   `-- spark.py
|-- ingestion/
|   `-- batch/
|       `-- load_orders_to_bronze.py
|-- transformations/
|   |-- bronze_to_silver/
|   |   `-- orders_silver.py
|   `-- silver_to_gold/
|       `-- daily_revenue.py
|-- docs/
|   |-- architecture.md
|   |-- roadmap.md
|   |-- decisions.md
|   |-- stabilization.md
|   `-- diagrams/
|       `-- module1-v1.mmd
|-- data/
|   |-- raw/
|   `-- warehouse/
|-- infra/
|   |-- docker-compose.yml
|   |-- spark/
|   `-- lab/
|-- scripts/
|-- notebooks/
`-- tests/
```

## Module Evolution Narrative

1. Module 1: Lakehouse Foundation (current local baseline)
2. Module 2: Storage Evolution (S3-compatible object storage)
3. Module 3: CDC Ingestion
4. Module 4: Streaming Analytics
5. Module 5: Metadata Intelligence
6. Module 6: AI Copilot

The design target is to keep medallion contracts and shared job interfaces stable while infrastructure capability increases module by module.

## Run Locally

Create local env file:

```bash
cp .env.example .env
```

### PowerShell

```powershell
.\scripts\run_job.ps1 up
.\scripts\run_job.ps1 bronze
.\scripts\run_job.ps1 silver
.\scripts\run_job.ps1 gold
.\scripts\run_job.ps1 down
```

### Git Bash / WSL

```bash
./scripts/run_job.sh up
./scripts/run_job.sh bronze
./scripts/run_job.sh silver
./scripts/run_job.sh gold
./scripts/run_job.sh down
```

## Optional Notebook Lab

PowerShell:

```powershell
.\scripts\run_lab.ps1 up
```

Git Bash / WSL:

```bash
./scripts/run_lab.sh up
```

Open `http://localhost:8888` and choose kernel **PySpark (NovaLake)**.

Stop lab:

```powershell
.\scripts\run_lab.ps1 down
```

```bash
./scripts/run_lab.sh down
```

## Validation Query

PowerShell:

```powershell
.\scripts\sql_shell.ps1 -Query "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date"
```

Git Bash / WSL:

```bash
./scripts/sql_shell.sh -q "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date"
```

## Quality Check

```bash
pytest -q
```
