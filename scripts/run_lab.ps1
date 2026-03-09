param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("up", "down", "logs")]
    [string]$Step
)

$envFile = ".env"
if (-not (Test-Path $envFile)) {
    Write-Error "Missing .env file at project root. Create it from .env.example first."
    Write-Host "Example: Copy-Item .env.example .env"
    exit 1
}

function Invoke-Compose {
    param([string[]]$Args)
    docker compose --env-file .env -f infra/docker-compose.yml --profile lab @Args
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

switch ($Step) {
    "up" {
        Invoke-Compose -Args @("up", "-d", "--build")
        Write-Host "Notebook Lab available at: http://localhost:8888"
    }
    "down" { Invoke-Compose -Args @("down") }
    "logs" { Invoke-Compose -Args @("logs", "-f", "notebook-lab") }
}
