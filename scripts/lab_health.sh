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

echo "[1/4] Checking notebook-lab container status..."
status="$(run_compose ps --format json notebook-lab | tr -d '\r\n')"
if [[ -z "$status" ]] || [[ "$status" != *"running"* ]]; then
  echo "FAIL: notebook-lab is not running."
  exit 1
fi
echo "OK: notebook-lab is running."

echo "[2/4] Checking HTTP endpoint http://localhost:8888 ..."
http_code="$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8888)"
if [[ "$http_code" != "200" ]] && [[ "$http_code" != "302" ]]; then
  echo "FAIL: Notebook endpoint returned HTTP $http_code"
  exit 1
fi
echo "OK: Notebook endpoint reachable (HTTP $http_code)."

echo "[3/4] Checking Spark master service from lab container..."
run_compose exec notebook-lab /bin/bash -lc "python3 - <<'PY'
import socket
s = socket.socket()
s.settimeout(5)
s.connect(('spark-master', 7077))
s.close()
print('OK: TCP connection to spark-master:7077')
PY"

echo "[4/4] Checking Iceberg catalog visibility..."
run_compose exec spark-master /opt/spark/bin/spark-sql \
  --conf spark.sql.catalogImplementation=in-memory \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.novalake=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.novalake.type=hadoop \
  --conf spark.sql.catalog.novalake.warehouse=/opt/novalake/data/warehouse \
  -e "SHOW NAMESPACES IN novalake;"

echo "Health check passed."
