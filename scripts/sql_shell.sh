#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="infra/docker-compose.yml"
ENV_FILE=".env"

usage() {
  echo "Usage:"
  echo "  ./scripts/sql_shell.sh                 # interactive shell"
  echo "  ./scripts/sql_shell.sh -q \"SELECT ...\""
  echo "  ./scripts/sql_shell.sh -f path/to/query.sql"
}

run_compose() {
  MSYS_NO_PATHCONV=1 docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing .env file at project root. Create it from .env.example first."
  echo "Example: cp .env.example .env"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

mapfile -t spark_conf_args < <(
  run_compose exec -T spark-master python /opt/novalake/scripts/spark_conf_cli.py
)

SPARK_SQL_BASE=(/opt/spark/bin/spark-sql)
SPARK_SQL_BASE+=("${spark_conf_args[@]}")

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
