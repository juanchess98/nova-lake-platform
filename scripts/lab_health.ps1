$ErrorActionPreference = "Stop"

Write-Host "[1/4] Checking notebook-lab container status..."
$statusJson = docker compose -f infra/docker-compose.yml --profile lab ps --format json notebook-lab
if (-not $statusJson) {
    Write-Error "FAIL: notebook-lab is not running."
    exit 1
}
if ($statusJson -notmatch '"State":"running"') {
    Write-Error "FAIL: notebook-lab is not running."
    exit 1
}
Write-Host "OK: notebook-lab is running."

Write-Host "[2/4] Checking HTTP endpoint http://localhost:8888 ..."
$resp = Invoke-WebRequest -Uri "http://localhost:8888" -UseBasicParsing -Method Get
if ($resp.StatusCode -ne 200) {
    Write-Error "FAIL: Notebook endpoint returned HTTP $($resp.StatusCode)"
    exit 1
}
Write-Host "OK: Notebook endpoint reachable (HTTP 200)."

Write-Host "[3/4] Checking Spark master service from lab container..."
docker compose -f infra/docker-compose.yml --profile lab exec notebook-lab /bin/bash -lc "python3 -c \"import socket;s=socket.socket();s.settimeout(5);s.connect(('spark-master',7077));s.close();print('OK: TCP connection to spark-master:7077')\""
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[4/4] Checking Iceberg catalog visibility..."
docker compose -f infra/docker-compose.yml --profile lab exec spark-master /opt/spark/bin/spark-sql --conf spark.sql.catalogImplementation=in-memory --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions --conf spark.sql.catalog.novalake=org.apache.iceberg.spark.SparkCatalog --conf spark.sql.catalog.novalake.type=hadoop --conf spark.sql.catalog.novalake.warehouse=/opt/novalake/data/warehouse -e "SHOW NAMESPACES IN novalake;"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Health check passed."
