# NovaLake System Requirements (Module 1 Baseline)

## Overview

This document defines the functional and nonfunctional requirements for the implemented NovaLake Module 1 baseline.

Module 1 scope is local-first and batch-oriented, with Spark + Iceberg medallion pipelines over deterministic synthetic commerce data.

## Functional Requirements

### FR-01 Data Generation

The platform must provide a reproducible synthetic commerce data generator that outputs six operational raw datasets:
- `customers`
- `products`
- `orders`
- `order_items`
- `payments`
- `shipments`

### FR-02 Raw Data Contract

The six datasets must be written as CSV files under `data/raw/` and documented in `metadata/datasets.yaml`.

### FR-03 Bronze Ingestion

The platform must ingest all six raw datasets into Iceberg Bronze tables (`novalake.bronze.*`) with ingestion metadata fields.

### FR-04 Silver Conformance

The platform must transform Bronze data into Silver tables (`novalake.silver.*`) with:
- standardized types and naming
- validation rules for statuses and monetary fields
- referential integrity across related entities

### FR-05 Gold Data Products

The platform must produce six Gold analytical datasets (`novalake.gold.*`):
- `daily_revenue`
- `sales_by_country`
- `top_products`
- `customer_revenue`
- `payment_success_rate`
- `shipment_delivery_summary`

### FR-06 Query and Exploration

Users must be able to query medallion layers via Spark SQL and explore outputs through the optional JupyterLab profile.

### FR-07 Environment Configuration Contract

Module 1 must require a project-root `.env` file (seeded from `.env.example`) for local credential/config loading in Docker Compose and operational scripts.

## Nonfunctional Requirements

### NFR-01 Reproducibility

Module 1 must be fully reproducible in a local containerized environment.

### NFR-02 Architectural Clarity

The platform must preserve explicit medallion layer boundaries and clear job responsibilities.

### NFR-03 Maintainability

Shared utilities must be reused for Spark/session/table behavior to reduce duplicated logic and improve consistency.

### NFR-04 Data Quality Baseline

Silver and Gold outputs must enforce core consistency checks (type integrity, arithmetic consistency, and entity references).

### NFR-05 Scope Discipline

Module 1 must remain intentionally simple and avoid introducing advanced infrastructure prematurely (for example MinIO, Kafka, Debezium, dbt).

### NFR-06 Evolution Readiness

Module 1 artifacts (docs, metadata contract, medallion naming, shared utilities) must support future module evolution without foundation redesign.

### NFR-07 Fail-Fast Configuration

Local operational scripts should fail fast when `.env` is missing to avoid ambiguous defaults and improve reproducibility.
