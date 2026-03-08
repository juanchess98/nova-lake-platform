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

$bronzeJobs = @(
    "/opt/novalake/ingestion/batch/load_customers_to_bronze.py",
    "/opt/novalake/ingestion/batch/load_products_to_bronze.py",
    "/opt/novalake/ingestion/batch/load_orders_to_bronze.py",
    "/opt/novalake/ingestion/batch/load_order_items_to_bronze.py",
    "/opt/novalake/ingestion/batch/load_payments_to_bronze.py",
    "/opt/novalake/ingestion/batch/load_shipments_to_bronze.py"
)

$silverJobs = @(
    "/opt/novalake/transformations/bronze_to_silver/customers_silver.py",
    "/opt/novalake/transformations/bronze_to_silver/products_silver.py",
    "/opt/novalake/transformations/bronze_to_silver/orders_silver.py",
    "/opt/novalake/transformations/bronze_to_silver/order_items_silver.py",
    "/opt/novalake/transformations/bronze_to_silver/payments_silver.py",
    "/opt/novalake/transformations/bronze_to_silver/shipments_silver.py"
)

$goldJobs = @(
    "/opt/novalake/transformations/silver_to_gold/daily_revenue.py",
    "/opt/novalake/transformations/silver_to_gold/sales_by_country.py",
    "/opt/novalake/transformations/silver_to_gold/top_products.py",
    "/opt/novalake/transformations/silver_to_gold/customer_revenue.py",
    "/opt/novalake/transformations/silver_to_gold/payment_success_rate.py",
    "/opt/novalake/transformations/silver_to_gold/shipment_delivery_summary.py"
)

function Invoke-Compose {
    param([string[]]$Args)
    docker compose -f infra/docker-compose.yml @Args
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Invoke-JobList {
    param([string[]]$JobPaths)
    foreach ($jobPath in $JobPaths) {
        Invoke-Compose -Args (@("exec", "spark-master") + $submitBase + @($jobPath))
    }
}

switch ($Step) {
    "build" { Invoke-Compose -Args @("build", "spark-master") }
    "up" { Invoke-Compose -Args @("up", "-d", "--build") }
    "down" {
        docker compose -f infra/docker-compose.yml --profile lab down --remove-orphans | Out-Null
        Invoke-Compose -Args @("down", "--remove-orphans")
    }
    "bronze" { Invoke-JobList -JobPaths $bronzeJobs }
    "silver" { Invoke-JobList -JobPaths $silverJobs }
    "gold" { Invoke-JobList -JobPaths $goldJobs }
    "all" {
        Invoke-JobList -JobPaths $bronzeJobs
        Invoke-JobList -JobPaths $silverJobs
        Invoke-JobList -JobPaths $goldJobs
    }
}
