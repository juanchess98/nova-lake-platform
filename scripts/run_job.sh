#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="infra/docker-compose.yml"
SPARK_SUBMIT="/opt/spark/bin/spark-submit --master spark://spark-master:7077"

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

case "$1" in
  build)
    run_compose build spark-master
    ;;
  up)
    run_compose up -d --build
    ;;
  down)
    run_compose down
    ;;
  bronze)
    run_compose exec spark-master /bin/bash -lc "$SPARK_SUBMIT /opt/novalake/ingestion/batch/load_orders_to_bronze.py"
    ;;
  silver)
    run_compose exec spark-master /bin/bash -lc "$SPARK_SUBMIT /opt/novalake/transformations/bronze_to_silver/orders_silver.py"
    ;;
  gold)
    run_compose exec spark-master /bin/bash -lc "$SPARK_SUBMIT /opt/novalake/transformations/silver_to_gold/daily_revenue.py"
    ;;
  all)
    run_compose exec spark-master /bin/bash -lc "$SPARK_SUBMIT /opt/novalake/ingestion/batch/load_orders_to_bronze.py"
    run_compose exec spark-master /bin/bash -lc "$SPARK_SUBMIT /opt/novalake/transformations/bronze_to_silver/orders_silver.py"
    run_compose exec spark-master /bin/bash -lc "$SPARK_SUBMIT /opt/novalake/transformations/silver_to_gold/daily_revenue.py"
    ;;
  *)
    usage
    exit 1
    ;;
esac
