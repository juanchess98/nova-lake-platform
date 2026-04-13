#!/usr/bin/env bash
set -euo pipefail

export PYSPARK_SUBMIT_ARGS="$(
  python /opt/novalake/scripts/spark_conf_cli.py \
    --format submit-args \
    --master spark://spark-master:7077 \
    --conf spark.cores.max=1 \
    --conf spark.executor.cores=1 \
    --include-pyspark-shell
)"

exec jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --ServerApp.token='' \
  --ServerApp.password='' \
  --ServerApp.root_dir=/opt/novalake/notebooks
