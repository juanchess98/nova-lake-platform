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

: "${NOVALAKE_S3_BUCKET:=novalake-lakehouse}"
: "${NOVALAKE_S3_WAREHOUSE_PREFIX:=warehouse}"
: "${NOVALAKE_S3_ACCESS_KEY:=novalake}"
: "${NOVALAKE_S3_SECRET_KEY:=novalake123}"
: "${NOVALAKE_S3_PATH_STYLE_ACCESS:=true}"

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
  --conf "spark.sql.catalog.novalake.warehouse=s3a://${NOVALAKE_S3_BUCKET}/${NOVALAKE_S3_WAREHOUSE_PREFIX}" \
  --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
  --conf spark.hadoop.fs.s3a.endpoint=minio:9000 \
  --conf "spark.hadoop.fs.s3a.access.key=${NOVALAKE_S3_ACCESS_KEY}" \
  --conf "spark.hadoop.fs.s3a.secret.key=${NOVALAKE_S3_SECRET_KEY}" \
  --conf "spark.hadoop.fs.s3a.path.style.access=${NOVALAKE_S3_PATH_STYLE_ACCESS}" \
  --conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
  --conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider \
  -e "SHOW NAMESPACES IN novalake;"

echo "Health check passed."
