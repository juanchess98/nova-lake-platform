$ErrorActionPreference = "Stop"

$envFile = ".env"
if (-not (Test-Path $envFile)) {
    Write-Error "Missing .env file at project root. Create it from .env.example first."
    Write-Host "Example: Copy-Item .env.example .env"
    exit 1
}

function Get-DotEnvValue {
    param(
        [string]$Name,
        [string]$DefaultValue = ""
    )

    $match = Get-Content $envFile |
        Where-Object { $_ -match "^\s*$Name=(.*)$" } |
        Select-Object -First 1

    if ($match) {
        return ($match -replace "^\s*$Name=", "").Trim()
    }

    return $DefaultValue
}

$bucket = Get-DotEnvValue -Name "NOVALAKE_S3_BUCKET" -DefaultValue "novalake-lakehouse"
$warehousePrefix = Get-DotEnvValue -Name "NOVALAKE_S3_WAREHOUSE_PREFIX" -DefaultValue "warehouse"
$accessKey = Get-DotEnvValue -Name "NOVALAKE_S3_ACCESS_KEY" -DefaultValue "novalake"
$secretKey = Get-DotEnvValue -Name "NOVALAKE_S3_SECRET_KEY" -DefaultValue "novalake123"
$pathStyle = Get-DotEnvValue -Name "NOVALAKE_S3_PATH_STYLE_ACCESS" -DefaultValue "true"

Write-Host "[1/4] Checking notebook-lab container status..."
$statusJson = docker compose --env-file .env -f infra/docker-compose.yml --profile lab ps --format json notebook-lab
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
docker compose --env-file .env -f infra/docker-compose.yml --profile lab exec notebook-lab /bin/bash -lc "python3 -c \"import socket;s=socket.socket();s.settimeout(5);s.connect(('spark-master',7077));s.close();print('OK: TCP connection to spark-master:7077')\""
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[4/4] Checking Iceberg catalog visibility..."
docker compose --env-file .env -f infra/docker-compose.yml --profile lab exec spark-master /opt/spark/bin/spark-sql --conf spark.sql.catalogImplementation=in-memory --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions --conf spark.sql.catalog.novalake=org.apache.iceberg.spark.SparkCatalog --conf spark.sql.catalog.novalake.type=hadoop --conf spark.sql.catalog.novalake.warehouse=s3a://$bucket/$warehousePrefix --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem --conf spark.hadoop.fs.s3a.endpoint=minio:9000 --conf spark.hadoop.fs.s3a.access.key=$accessKey --conf spark.hadoop.fs.s3a.secret.key=$secretKey --conf spark.hadoop.fs.s3a.path.style.access=$pathStyle --conf spark.hadoop.fs.s3a.connection.ssl.enabled=false --conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider -e "SHOW NAMESPACES IN novalake;"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Health check passed."
