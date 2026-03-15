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
    param([string[]]$ComposeArgs)
    docker compose --env-file .env -f infra/docker-compose.yml --profile lab @ComposeArgs
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

switch ($Step) {
    "up" {
        Invoke-Compose -ComposeArgs @("up", "-d", "--build")
        Write-Host "Notebook Lab available at: http://localhost:8888"
    }
    "down" { Invoke-Compose -ComposeArgs @("down") }
    "logs" { Invoke-Compose -ComposeArgs @("logs", "-f", "notebook-lab") }
}
