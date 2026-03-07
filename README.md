# NovaLake Platform

NovaLake Platform is a portfolio-grade data platform project focused on architecture quality, modularity, and extensibility.

Current release implements **Module 1: Lakehouse Foundation**.

## Scope

- Dockerized local environment
- Spark processing with Apache Iceberg tables
- E-commerce sample datasets
- Medallion data model (`bronze`, `silver`, `gold`)
- Batch flow: `orders` raw -> bronze -> silver -> gold
- ADR-based architecture documentation

Out of scope in Module 1: Kafka, Debezium, Airflow, dbt, observability stack, AI modules.

## Repository Layout

```text
nova-lake-platform/
|-- core/
|   |-- config.py
|   `-- spark.py
|-- data/
|   |-- raw/
|   |   |-- customers.csv
|   |   |-- products.csv
|   |   |-- orders.csv
|   |   `-- order_items.csv
|   `-- warehouse/
|       `-- .gitkeep
|-- docs/
|   |-- architecture.md
|   |-- decisions.md
|   `-- stabilization.md
|-- infra/
|   |-- docker-compose.yml
|   |-- lab/
|   |   `-- Dockerfile
|   `-- spark/
|       `-- Dockerfile
|-- ingestion/
|   `-- batch/
|       `-- load_orders_to_bronze.py
|-- transformations/
|   |-- bronze_to_silver/
|   |   `-- orders_silver.py
|   `-- silver_to_gold/
|       `-- daily_revenue.py
|-- scripts/
|   |-- lab_health.ps1
|   |-- lab_health.sh
|   |-- run_lab.ps1
|   |-- run_lab.sh
|   |-- run_job.ps1
|   |-- run_job.sh
|   |-- sql_shell.ps1
|   `-- sql_shell.sh
|-- notebooks/
|   |-- 01_lakehouse_exploration.ipynb
|   `-- README.md
|-- tests/
|   `-- test_project_structure.py
|-- metadata/
|   `-- datasets.yaml
|-- sql/
|   `-- postgres_init/
|       `-- 001_init_ops_schema.sql
|-- .gitignore
|-- Makefile
`-- requirements.txt
```

## Architecture Notes

- `infra/spark/Dockerfile` builds a custom Spark image with Iceberg runtime JAR pre-bundled.
- Spark jobs submit to the standalone Spark master (`spark://spark-master:7077`), so master/worker topology is actually used.
- Iceberg catalog is local Hadoop catalog at `data/warehouse`.
- Python path resolution is standardized using container `PYTHONPATH=/opt/novalake`.
- Notebook UX is isolated in an optional `lab` profile and does not replace production pipeline code.

## Run Locally

### PowerShell (recommended on Windows)

```powershell
.\scripts\run_job.ps1 up
.\scripts\run_job.ps1 bronze
.\scripts\run_job.ps1 silver
.\scripts\run_job.ps1 gold
```

Stop services:

```powershell
.\scripts\run_job.ps1 down
```

Open interactive SQL shell:

```powershell
.\scripts\sql_shell.ps1
```

Run one query:

```powershell
.\scripts\sql_shell.ps1 -Query "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date"
```

### Git Bash / WSL

```bash
./scripts/run_job.sh up
./scripts/run_job.sh bronze
./scripts/run_job.sh silver
./scripts/run_job.sh gold
```

Stop services:

```bash
./scripts/run_job.sh down
```

### Optional Notebook Lab

PowerShell:

```powershell
.\scripts\run_lab.ps1 up
```

Git Bash / WSL:

```bash
./scripts/run_lab.sh up
```

Then open: `http://localhost:8888`

In JupyterLab, select kernel: **PySpark (NovaLake)**.
This kernel is preconfigured for:
- Spark master: `spark://spark-master:7077`
- Iceberg catalog: `novalake`
- Warehouse: `/opt/novalake/data/warehouse`
- Starter notebook: `notebooks/01_lakehouse_exploration.ipynb`

Stop lab:

```powershell
.\scripts\run_lab.ps1 down
```

```bash
./scripts/run_lab.sh down
```

Open interactive SQL shell:

```bash
./scripts/sql_shell.sh
```

Run one query:

```bash
./scripts/sql_shell.sh -q "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date"
```

## Makefile Shortcuts

If GNU Make is installed:

```bash
make build
make up
make bronze
make silver
make gold
make down
make lab-up
make lab-logs
make lab-down
make lab-health
```

## Validation Query (direct)

```bash
MSYS_NO_PATHCONV=1 docker compose -f infra/docker-compose.yml exec spark-master /opt/spark/bin/spark-sql \
  --conf spark.sql.catalogImplementation=in-memory \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.novalake=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.novalake.type=hadoop \
  --conf spark.sql.catalog.novalake.warehouse=/opt/novalake/data/warehouse \
  -e "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date;"
```

## Troubleshooting

- `make: command not found`:
  - Use `run_job.ps1` or `run_job.sh`, or install GNU Make.
- `exec: C:/Program Files/Git/opt/...`:
  - Git Bash path conversion issue; use `run_job.sh` (already handles `MSYS_NO_PATHCONV=1`).
- `SparkCatalog class not found`:
  - Re-run `up` (or `build`) to rebuild the custom Spark image with Iceberg JAR.
- `ERROR XSDB6 ... metastore_db`:
  - Cause: Hive Derby metastore lock contention.
  - Action: use `scripts/sql_shell.*` (already sets `spark.sql.catalogImplementation=in-memory`) and avoid multiple concurrent `spark-sql` sessions.
- Notebook cannot connect to Spark catalog:
  - Ensure core services are up, lab image was rebuilt (`run_lab ... up`), and notebook uses the **PySpark (NovaLake)** kernel.

## Lab Health Check

PowerShell:

```powershell
.\scripts\lab_health.ps1
```

Git Bash / WSL:

```bash
./scripts/lab_health.sh
```

This validates:
- notebook-lab container state
- notebook HTTP endpoint (`localhost:8888`)
- TCP connectivity from notebook to Spark master
- Iceberg catalog visibility (`SHOW NAMESPACES IN novalake`)

## Stabilization History

See [docs/stabilization.md](docs/stabilization.md) for a detailed log of initial integration difficulties and the final fixes applied.

## Roadmap

1. Postgres incremental ingestion
2. Kafka + Debezium CDC ingestion
3. Orchestration and data contracts
4. Semantic modeling layer
5. Observability and AI-assisted platform operations
