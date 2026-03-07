param(
    [string]$Query,
    [string]$File
)

$baseArgs = @(
    "exec", "spark-master",
    "/opt/spark/bin/spark-sql",
    "--conf", "spark.sql.catalogImplementation=in-memory",
    "--conf", "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    "--conf", "spark.sql.catalog.novalake=org.apache.iceberg.spark.SparkCatalog",
    "--conf", "spark.sql.catalog.novalake.type=hadoop",
    "--conf", "spark.sql.catalog.novalake.warehouse=/opt/novalake/data/warehouse"
)

if ($Query -and $File) {
    Write-Error "Use either -Query or -File, not both."
    exit 1
}

if ($Query) {
    docker compose -f infra/docker-compose.yml @baseArgs -e $Query
    exit $LASTEXITCODE
}

if ($File) {
    docker compose -f infra/docker-compose.yml @baseArgs -f $File
    exit $LASTEXITCODE
}

docker compose -f infra/docker-compose.yml @baseArgs
exit $LASTEXITCODE
