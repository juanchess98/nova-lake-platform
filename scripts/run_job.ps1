param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("build", "up", "down", "bronze", "silver", "gold", "all")]
    [string]$Step
)

$submitBase = @(
    "/opt/spark/bin/spark-submit",
    "--master",
    "spark://spark-master:7077"
)

function Invoke-Compose {
    param([string[]]$Args)
    docker compose -f infra/docker-compose.yml @Args
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

switch ($Step) {
    "build" { Invoke-Compose -Args @("build", "spark-master") }
    "up" { Invoke-Compose -Args @("up", "-d", "--build") }
    "down" { Invoke-Compose -Args @("down") }
    "bronze" { Invoke-Compose -Args (@("exec", "spark-master") + $submitBase + @("/opt/novalake/ingestion/batch/load_orders_to_bronze.py")) }
    "silver" { Invoke-Compose -Args (@("exec", "spark-master") + $submitBase + @("/opt/novalake/transformations/bronze_to_silver/orders_silver.py")) }
    "gold" { Invoke-Compose -Args (@("exec", "spark-master") + $submitBase + @("/opt/novalake/transformations/silver_to_gold/daily_revenue.py")) }
    "all" {
        Invoke-Compose -Args (@("exec", "spark-master") + $submitBase + @("/opt/novalake/ingestion/batch/load_orders_to_bronze.py"))
        Invoke-Compose -Args (@("exec", "spark-master") + $submitBase + @("/opt/novalake/transformations/bronze_to_silver/orders_silver.py"))
        Invoke-Compose -Args (@("exec", "spark-master") + $submitBase + @("/opt/novalake/transformations/silver_to_gold/daily_revenue.py"))
    }
}
