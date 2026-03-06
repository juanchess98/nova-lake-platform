# NovaLake Platform

NovaLake Platform is a portfolio-grade data platform project designed to demonstrate architecture, data engineering fundamentals, and modular platform evolution.

Current release focuses on **Module 1: Lakehouse Foundation**.

## Why This Project Exists

Most portfolio projects show isolated tools. This one is intentionally different:

- Architecture-first, not notebook-first
- Modular roadmap for incremental platform growth
- Production-minded conventions (layering, naming, metadata, ADRs)
- Local reproducibility for fast iteration

The target audience is engineering hiring managers evaluating senior/staff data platform potential.

## Module 1 Scope (Implemented)

- Local stack with Docker Compose
- Spark processing with Apache Iceberg tables
- E-commerce sample domain
- Medallion model: Bronze -> Silver -> Gold
- Batch pipeline for `orders`
- Dataset metadata contract
- ADR-based architecture documentation

Out of scope in this module:

- Kafka / Debezium / CDC streaming
- Airflow orchestration
- dbt semantic modeling
- Observability stack
- AI copilots

## Architecture Snapshot

```text
data/raw/*.csv
     |
     v
ingestion/batch/load_orders_to_bronze.py
     |
     v
novalake.bronze.orders (Iceberg)
     |
     v
transformations/bronze_to_silver/orders_silver.py
     |
     v
novalake.silver.orders (typed + validated)
     |
     v
transformations/silver_to_gold/daily_revenue.py
     |
     v
novalake.gold.daily_revenue (business aggregate)
```

Core design choices:

- **Catalog:** `novalake`
- **Namespaces:** `bronze`, `silver`, `gold`
- **Warehouse path:** `data/warehouse`
- **Shared runtime utilities:** `core/config.py`, `core/spark.py`

## Repository Structure

```text
nova-lake-platform/
|-- core/
|   |-- config.py
|   `-- spark.py
|-- data/
|   |-- warehouse/
|   `-- raw/
|       |-- customers.csv
|       |-- products.csv
|       |-- orders.csv
|       `-- order_items.csv
|-- docs/
|   |-- architecture.md
|   `-- decisions.md
|-- infra/
|   `-- docker-compose.yml
|-- ingestion/
|   `-- batch/
|       `-- load_orders_to_bronze.py
|-- metadata/
|   `-- datasets.yaml
|-- sql/
|   `-- postgres_init/
|       `-- 001_init_ops_schema.sql
|-- transformations/
|   |-- bronze_to_silver/
|   |   `-- orders_silver.py
|   `-- silver_to_gold/
|       `-- daily_revenue.py
|-- tests/
|   `-- test_project_structure.py
|-- .gitignore
|-- Makefile
`-- requirements.txt
```

## Local Run

Preferred workflow:

```bash
make up
```

Equivalent direct command:

```bash
docker compose -f infra/docker-compose.yml up -d
```

1. Ingest raw orders into Bronze:

```bash
make bronze
```

2. Build Silver orders:

```bash
make silver
```

3. Build Gold daily revenue:

```bash
make gold
```

4. Stop services when done:

```bash
make down
```

5. Optional validation query:

```bash
docker compose -f infra/docker-compose.yml exec spark-master spark-sql \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.novalake=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.novalake.type=hadoop \
  --conf spark.sql.catalog.novalake.warehouse=/opt/novalake/data/warehouse \
  -e "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date;"
```

## Engineering Notes

- Sample datasets are internally consistent across primary/foreign keys.
- Silver transformation applies lightweight quality filters and deterministic deduplication.
- Naming conventions are consistent across scripts, namespaces, and table identifiers.
- Runtime helpers are centralized, making future modules additive instead of disruptive.

## Roadmap (Planned Modules)

1. Operational ingestion expansion (Postgres incremental loads)
2. CDC/streaming ingestion (Kafka + Debezium)
3. Orchestration and contracts (Airflow + quality gates)
4. Semantic consumption layer (dbt-style curated marts)
5. Observability and AI-assisted platform operations
