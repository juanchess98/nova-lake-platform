param(
    [string]$Query,
    [string]$File
)

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

$baseArgs = @(
    "exec", "spark-master",
    "/opt/spark/bin/spark-sql",
    "--conf", "spark.sql.catalogImplementation=in-memory",
    "--conf", "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    "--conf", "spark.sql.catalog.novalake=org.apache.iceberg.spark.SparkCatalog",
    "--conf", "spark.sql.catalog.novalake.type=hadoop",
    "--conf", "spark.sql.catalog.novalake.warehouse=s3a://$bucket/$warehousePrefix",
    "--conf", "spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem",
    "--conf", "spark.hadoop.fs.s3a.endpoint=minio:9000",
    "--conf", "spark.hadoop.fs.s3a.access.key=$accessKey",
    "--conf", "spark.hadoop.fs.s3a.secret.key=$secretKey",
    "--conf", "spark.hadoop.fs.s3a.path.style.access=$pathStyle",
    "--conf", "spark.hadoop.fs.s3a.connection.ssl.enabled=false",
    "--conf", "spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
)

if ($Query -and $File) {
    Write-Error "Use either -Query or -File, not both."
    exit 1
}

if ($Query) {
    docker compose --env-file .env -f infra/docker-compose.yml @baseArgs -e $Query
    exit $LASTEXITCODE
}

if ($File) {
    docker compose --env-file .env -f infra/docker-compose.yml @baseArgs -f $File
    exit $LASTEXITCODE
}

docker compose --env-file .env -f infra/docker-compose.yml @baseArgs
exit $LASTEXITCODE
