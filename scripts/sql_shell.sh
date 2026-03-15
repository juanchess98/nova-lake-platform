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

: "${NOVALAKE_S3_BUCKET:=novalake-lakehouse}"
: "${NOVALAKE_S3_WAREHOUSE_PREFIX:=warehouse}"
: "${NOVALAKE_S3_ACCESS_KEY:=novalake}"
: "${NOVALAKE_S3_SECRET_KEY:=novalake123}"
: "${NOVALAKE_S3_PATH_STYLE_ACCESS:=true}"

SPARK_SQL_BASE=(
  /opt/spark/bin/spark-sql
  --conf spark.sql.catalogImplementation=in-memory
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
  --conf spark.sql.catalog.novalake=org.apache.iceberg.spark.SparkCatalog
  --conf spark.sql.catalog.novalake.type=hadoop
  --conf "spark.sql.catalog.novalake.warehouse=s3a://${NOVALAKE_S3_BUCKET}/${NOVALAKE_S3_WAREHOUSE_PREFIX}"
  --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
  --conf spark.hadoop.fs.s3a.endpoint=minio:9000
  --conf "spark.hadoop.fs.s3a.access.key=${NOVALAKE_S3_ACCESS_KEY}"
  --conf "spark.hadoop.fs.s3a.secret.key=${NOVALAKE_S3_SECRET_KEY}"
  --conf "spark.hadoop.fs.s3a.path.style.access=${NOVALAKE_S3_PATH_STYLE_ACCESS}"
  --conf spark.hadoop.fs.s3a.connection.ssl.enabled=false
  --conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider
)

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
