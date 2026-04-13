#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="infra/docker-compose.yml"
ENV_FILE=".env"

run_compose() {
  MSYS_NO_PATHCONV=1 docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" --profile lab "$@"
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
  run_compose exec -T spark-master python /opt/novalake/scripts/spark_conf_cli.py --target spark-sql
)

: "${NOVALAKE_CATALOG_URI:=http://localhost:19120/api/v1}"

echo "[1/6] Checking notebook-lab container status..."
status="$(run_compose ps --format json notebook-lab | tr -d '\r\n')"
if [[ -z "$status" ]] || [[ "$status" != *"running"* ]]; then
  echo "FAIL: notebook-lab is not running."
  exit 1
fi
echo "OK: notebook-lab is running."

echo "[2/6] Checking HTTP endpoint http://localhost:8888 ..."
http_code="$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8888)"
if [[ "$http_code" != "200" ]] && [[ "$http_code" != "302" ]]; then
  echo "FAIL: Notebook endpoint returned HTTP $http_code"
  exit 1
fi
echo "OK: Notebook endpoint reachable (HTTP $http_code)."

echo "[3/6] Checking Spark master service from lab container..."
run_compose exec notebook-lab /bin/bash -lc "python3 - <<'PY'
import socket
s = socket.socket()
s.settimeout(5)
s.connect(('spark-master', 7077))
s.close()
print('OK: TCP connection to spark-master:7077')
PY"

echo "[4/6] Checking Nessie endpoint ${NOVALAKE_CATALOG_URI}/config ..."
nessie_http_code="$(curl -s -o /dev/null -w "%{http_code}" "${NOVALAKE_CATALOG_URI}/config")"
if [[ "$nessie_http_code" != "200" ]]; then
  echo "FAIL: Nessie endpoint returned HTTP $nessie_http_code"
  exit 1
fi
echo "OK: Nessie endpoint reachable (HTTP 200)."

echo "[5/6] Checking Iceberg catalog visibility..."
run_compose exec spark-master /opt/spark/bin/spark-sql "${spark_conf_args[@]}" -e "SHOW NAMESPACES IN novalake;"

echo "[6/6] Checking representative Gold query..."
run_compose exec spark-master /opt/spark/bin/spark-sql "${spark_conf_args[@]}" -e \
  "SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date LIMIT 5;"

echo "Health check passed."
