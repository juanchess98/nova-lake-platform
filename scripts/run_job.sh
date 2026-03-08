#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="infra/docker-compose.yml"
SPARK_SUBMIT="/opt/spark/bin/spark-submit --master spark://spark-master:7077"

BRONZE_JOBS=(
  "/opt/novalake/ingestion/batch/load_customers_to_bronze.py"
  "/opt/novalake/ingestion/batch/load_products_to_bronze.py"
  "/opt/novalake/ingestion/batch/load_orders_to_bronze.py"
  "/opt/novalake/ingestion/batch/load_order_items_to_bronze.py"
  "/opt/novalake/ingestion/batch/load_payments_to_bronze.py"
  "/opt/novalake/ingestion/batch/load_shipments_to_bronze.py"
)

SILVER_JOBS=(
  "/opt/novalake/transformations/bronze_to_silver/customers_silver.py"
  "/opt/novalake/transformations/bronze_to_silver/products_silver.py"
  "/opt/novalake/transformations/bronze_to_silver/orders_silver.py"
  "/opt/novalake/transformations/bronze_to_silver/order_items_silver.py"
  "/opt/novalake/transformations/bronze_to_silver/payments_silver.py"
  "/opt/novalake/transformations/bronze_to_silver/shipments_silver.py"
)

GOLD_JOBS=(
  "/opt/novalake/transformations/silver_to_gold/daily_revenue.py"
  "/opt/novalake/transformations/silver_to_gold/sales_by_country.py"
  "/opt/novalake/transformations/silver_to_gold/top_products.py"
  "/opt/novalake/transformations/silver_to_gold/customer_revenue.py"
  "/opt/novalake/transformations/silver_to_gold/payment_success_rate.py"
  "/opt/novalake/transformations/silver_to_gold/shipment_delivery_summary.py"
)

usage() {
  echo "Usage: ./scripts/run_job.sh {build|up|down|bronze|silver|gold|all}"
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

run_compose() {
  MSYS_NO_PATHCONV=1 docker compose -f "$COMPOSE_FILE" "$@"
}

run_jobs() {
  local -n jobs_ref=$1
  for job in "${jobs_ref[@]}"; do
    run_compose exec spark-master /bin/bash -lc "$SPARK_SUBMIT $job"
  done
}

case "$1" in
  build)
    run_compose build spark-master
    ;;
  up)
    run_compose up -d --build
    ;;
  down)
    run_compose --profile lab down --remove-orphans || true
    run_compose down --remove-orphans
    ;;
  bronze)
    run_jobs BRONZE_JOBS
    ;;
  silver)
    run_jobs SILVER_JOBS
    ;;
  gold)
    run_jobs GOLD_JOBS
    ;;
  all)
    run_jobs BRONZE_JOBS
    run_jobs SILVER_JOBS
    run_jobs GOLD_JOBS
    ;;
  *)
    usage
    exit 1
    ;;
esac
