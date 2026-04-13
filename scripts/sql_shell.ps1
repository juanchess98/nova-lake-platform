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

$sparkConfArgs = @(
    docker compose --env-file .env -f infra/docker-compose.yml exec -T spark-master python /opt/novalake/scripts/spark_conf_cli.py --target spark-sql
)
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$baseArgs = @(
    "exec", "spark-master",
    "/opt/spark/bin/spark-sql"
)

$baseArgs += $sparkConfArgs

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
