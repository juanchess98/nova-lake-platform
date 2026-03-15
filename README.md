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

## Platform Initialization Guide

This is the recommended local initialization flow for Module 2. It is written to keep startup deterministic, observable, and easy to repeat.

Validated locally on March 15, 2026:
- `.\scripts\run_job.ps1 up`
- `.\scripts\run_job.ps1 bronze`
- `.\scripts\run_job.ps1 silver`
- `.\scripts\run_job.ps1 gold`
- `.\scripts\lab_health.ps1`
- `.\scripts\run_job.ps1 down`

The PowerShell helper scripts are the recommended entrypoint on Windows.

### Step 0. Confirm local prerequisites

Before starting the stack, make sure:

- Docker Desktop or Docker Engine with Docker Compose v2 is installed and running
- the following ports are free on your machine:
  - `5432` for PostgreSQL
  - `7077`, `8080`, `8081` for Spark
  - `8888` for JupyterLab
  - `9000`, `9001` for MinIO API and console
- you are in the project root
- you are on the expected branch for Module 2 work

Best practice:
- treat the local stack as an environment, not just a command sequence
- confirm Docker is healthy before starting jobs
- avoid editing credentials directly in scripts; keep them in `.env`

### Step 1. Create the environment file

NovaLake requires a project-root `.env` file before running any `run_*`, `sql_shell`, or `lab_health` script.

PowerShell:
```powershell
Copy-Item .env.example .env
```

Bash:
```bash
cp .env.example .env
```

Then review the values in `.env`:

- PostgreSQL credentials
- `NOVALAKE_STORAGE_BACKEND=s3_compatible`
- MinIO access key / secret key
- Iceberg warehouse bucket and prefix

DataOps note:
- do not commit `.env`
- if `.env` already exists from an earlier setup, merge in the new MinIO variables from `.env.example` rather than replacing blindly

### Step 2. Build and start the platform services

This starts PostgreSQL, Spark, and MinIO. The startup command also builds the custom Spark image with Iceberg and S3A dependencies.

PowerShell:
```powershell
.\scripts\run_job.ps1 up
```

Bash:
```bash
./scripts/run_job.sh up
```

Service endpoints after startup:

- Spark master UI: `http://localhost:8080`
- Spark worker UI: `http://localhost:8081`
- MinIO API: `http://localhost:9000`
- MinIO console: `http://localhost:9001`

Optional direct status check:

```powershell
docker compose --env-file .env -f infra/docker-compose.yml ps
```

```bash
docker compose --env-file .env -f infra/docker-compose.yml ps
```

Best practice:
- always wait for services to settle before running Spark jobs
- confirm MinIO is reachable before expecting Iceberg tables to be written
- on Windows, prefer the PowerShell wrappers over raw `docker compose` commands for repeatable local operations

### Step 3. Initialize the medallion pipeline

For first-time platform initialization, run the pipeline layer by layer. This makes failures easier to isolate and follows a cleaner DataOps workflow than jumping straight to `all`.

Bronze:

PowerShell:
```powershell
.\scripts\run_job.ps1 bronze
```

Bash:
```bash
./scripts/run_job.sh bronze
```

Silver:

PowerShell:
```powershell
.\scripts\run_job.ps1 silver
```

Bash:
```bash
./scripts/run_job.sh silver
```

Gold:

PowerShell:
```powershell
.\scripts\run_job.ps1 gold
```

Bash:
```bash
./scripts/run_job.sh gold
```

For repeat runs, the full pipeline shortcut is available:

PowerShell:
```powershell
.\scripts\run_job.ps1 all
```

Bash:
```bash
./scripts/run_job.sh all
```

### Step 4. Validate the platform state

First, confirm the catalog is visible:

PowerShell:
```powershell
.\scripts\sql_shell.ps1 -Query "SHOW NAMESPACES IN novalake"
```

Bash:
```bash
./scripts/sql_shell.sh -q "SHOW NAMESPACES IN novalake"
```

Then validate that a gold data product is queryable:

PowerShell:
```powershell
.\scripts\sql_shell.ps1 -Query "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date"
```

Bash:
```bash
./scripts/sql_shell.sh -q "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date"
```

Finally, inspect MinIO:

- open `http://localhost:9001`
- sign in with `NOVALAKE_S3_ACCESS_KEY` and `NOVALAKE_S3_SECRET_KEY` from `.env`
- verify bucket `novalake-lakehouse` exists
- verify the `warehouse/` prefix contains Iceberg-managed table data for `bronze`, `silver`, and `gold`

Best practice:
- validate both the catalog view and the physical storage view
- check storage after the first successful run to confirm compute and storage are correctly separated

### Step 5. Start the optional notebook lab

PowerShell:
```powershell
.\scripts\run_lab.ps1 up
```

Bash:
```bash
./scripts/run_lab.sh up
```

Then open `http://localhost:8888` and use kernel **PySpark (NovaLake)**.

Optional health check for the lab profile:

PowerShell:
```powershell
.\scripts\lab_health.ps1
```

Bash:
```bash
./scripts/lab_health.sh
```

What a healthy result looks like:
- notebook-lab is running
- `http://localhost:8888` responds successfully
- notebook-lab can reach `spark-master:7077`
- Spark SQL returns the `bronze`, `silver`, and `gold` namespaces
- the script ends with `Health check passed.`

### Step 6. Stop the platform cleanly

When you are done, stop the services to avoid leaving containers and ports running in the background.

PowerShell:
```powershell
.\scripts\run_job.ps1 down
```

Bash:
```bash
./scripts/run_job.sh down
```

Best practice:
- shut the stack down cleanly between major config changes
- rebuild after dependency or Dockerfile changes to keep environments reproducible
- treat `down` as part of the operational workflow, not just cleanup, because it confirms containers and the network can be removed cleanly

### Quick start summary

If you want the shortest safe sequence:

1. Copy `.env.example` to `.env`
2. Run `.\scripts\run_job.ps1 up` or `./scripts/run_job.sh up`
3. Run `bronze`, then `silver`, then `gold`
4. Validate with `SHOW NAMESPACES IN novalake`
5. Check MinIO at `http://localhost:9001`

## Module Evolution

- Module 1: Lakehouse Foundation
- Module 2: Storage Evolution (current baseline)
- Module 3: CDC Ingestion
- Module 4: Streaming Analytics
- Module 5: Metadata Intelligence
- Module 6: AI Copilot
