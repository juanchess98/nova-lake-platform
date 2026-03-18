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

$sparkConfArgs = @(
    docker compose --env-file .env -f infra/docker-compose.yml exec -T spark-master python /opt/novalake/scripts/spark_conf_cli.py
)
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$catalogUri = Get-DotEnvValue -Name "NOVALAKE_CATALOG_URI" -DefaultValue "http://localhost:19120/api/v1"

Write-Host "[1/5] Checking notebook-lab container status..."
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

Write-Host "[2/5] Checking HTTP endpoint http://localhost:8888 ..."
$resp = Invoke-WebRequest -Uri "http://localhost:8888" -UseBasicParsing -Method Get
if ($resp.StatusCode -ne 200) {
    Write-Error "FAIL: Notebook endpoint returned HTTP $($resp.StatusCode)"
    exit 1
}
Write-Host "OK: Notebook endpoint reachable (HTTP 200)."

Write-Host "[3/5] Checking Spark master service from lab container..."
$sparkConnectivityCheck = 'echo > /dev/tcp/spark-master/7077 && echo "OK: TCP connection to spark-master:7077"'
$composeArgs = @(
    "compose",
    "--env-file", ".env",
    "-f", "infra/docker-compose.yml",
    "--profile", "lab",
    "exec", "notebook-lab",
    "/bin/bash", "-lc",
    $sparkConnectivityCheck
)
& docker @composeArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[4/5] Checking Nessie endpoint $catalogUri/config ..."
$nessieResp = Invoke-WebRequest -Uri "$catalogUri/config" -UseBasicParsing -Method Get
if ($nessieResp.StatusCode -ne 200) {
    Write-Error "FAIL: Nessie endpoint returned HTTP $($nessieResp.StatusCode)"
    exit 1
}
Write-Host "OK: Nessie endpoint reachable (HTTP 200)."

Write-Host "[5/5] Checking Iceberg catalog visibility..."
$catalogCheckArgs = @(
    "compose",
    "--env-file", ".env",
    "-f", "infra/docker-compose.yml",
    "--profile", "lab",
    "exec", "spark-master",
    "/opt/spark/bin/spark-sql"
)
$catalogCheckArgs += $sparkConfArgs
$catalogCheckArgs += @("-e", "SHOW NAMESPACES IN novalake;")
& docker @catalogCheckArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Health check passed."
