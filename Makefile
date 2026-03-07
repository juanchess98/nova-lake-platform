COMPOSE_FILE := infra/docker-compose.yml
COMPOSE := MSYS_NO_PATHCONV=1 docker compose -f $(COMPOSE_FILE)
SPARK_SUBMIT := /opt/spark/bin/spark-submit --master spark://spark-master:7077

.PHONY: up down build bronze silver gold lab-up lab-down lab-logs lab-health

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) --profile lab down --remove-orphans || true
	$(COMPOSE) down --remove-orphans

build:
	$(COMPOSE) build spark-master

bronze:
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/ingestion/batch/load_orders_to_bronze.py

silver:
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/bronze_to_silver/orders_silver.py

gold:
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/silver_to_gold/daily_revenue.py

lab-up:
	$(COMPOSE) --profile lab up -d --build

lab-down:
	$(COMPOSE) --profile lab down

lab-logs:
	$(COMPOSE) --profile lab logs -f notebook-lab

lab-health:
	./scripts/lab_health.sh
