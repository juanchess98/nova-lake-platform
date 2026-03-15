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
	$(COMPOSE) build spark-master notebook-lab

bronze:
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/ingestion/batch/load_customers_to_bronze.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/ingestion/batch/load_products_to_bronze.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/ingestion/batch/load_orders_to_bronze.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/ingestion/batch/load_order_items_to_bronze.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/ingestion/batch/load_payments_to_bronze.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/ingestion/batch/load_shipments_to_bronze.py

silver:
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/bronze_to_silver/customers_silver.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/bronze_to_silver/products_silver.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/bronze_to_silver/orders_silver.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/bronze_to_silver/order_items_silver.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/bronze_to_silver/payments_silver.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/bronze_to_silver/shipments_silver.py

gold:
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/silver_to_gold/daily_revenue.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/silver_to_gold/sales_by_country.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/silver_to_gold/top_products.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/silver_to_gold/customer_revenue.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/silver_to_gold/payment_success_rate.py
	$(COMPOSE) exec spark-master $(SPARK_SUBMIT) /opt/novalake/transformations/silver_to_gold/shipment_delivery_summary.py

lab-up:
	$(COMPOSE) --profile lab up -d --build

lab-down:
	$(COMPOSE) --profile lab down

lab-logs:
	$(COMPOSE) --profile lab logs -f notebook-lab

lab-health:
	./scripts/lab_health.sh
