#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="infra/docker-compose.yml"
SPARK_SQL_BASE=(
  /opt/spark/bin/spark-sql
  --conf spark.sql.catalogImplementation=in-memory
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
  --conf spark.sql.catalog.novalake=org.apache.iceberg.spark.SparkCatalog
  --conf spark.sql.catalog.novalake.type=hadoop
  --conf spark.sql.catalog.novalake.warehouse=/opt/novalake/data/warehouse
)

usage() {
  echo "Usage:"
  echo "  ./scripts/sql_shell.sh                 # interactive shell"
  echo "  ./scripts/sql_shell.sh -q \"SELECT ...\""
  echo "  ./scripts/sql_shell.sh -f path/to/query.sql"
}

run_compose() {
  MSYS_NO_PATHCONV=1 docker compose -f "$COMPOSE_FILE" "$@"
}

if [[ $# -eq 0 ]]; then
  run_compose exec spark-master "${SPARK_SQL_BASE[@]}"
  exit 0
fi

case "$1" in
  -q)
    [[ $# -eq 2 ]] || { usage; exit 1; }
    run_compose exec spark-master "${SPARK_SQL_BASE[@]}" -e "$2"
    ;;
  -f)
    [[ $# -eq 2 ]] || { usage; exit 1; }
    run_compose exec spark-master "${SPARK_SQL_BASE[@]}" -f "$2"
    ;;
  *)
    usage
    exit 1
    ;;
esac
