COMPOSE_FILE := infra/docker-compose.yml
COMPOSE := docker compose -f $(COMPOSE_FILE)

.PHONY: up down bronze silver gold

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

bronze:
	$(COMPOSE) exec spark-master spark-submit /opt/novalake/ingestion/batch/load_orders_to_bronze.py

silver:
	$(COMPOSE) exec spark-master spark-submit /opt/novalake/transformations/bronze_to_silver/orders_silver.py

gold:
	$(COMPOSE) exec spark-master spark-submit /opt/novalake/transformations/silver_to_gold/daily_revenue.py
