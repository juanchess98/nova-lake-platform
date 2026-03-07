param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("up", "down", "logs")]
    [string]$Step
)

function Invoke-Compose {
    param([string[]]$Args)
    docker compose -f infra/docker-compose.yml --profile lab @Args
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
