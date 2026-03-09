# Notebook Lab (Optional)

This folder is for exploratory analytics and demo notebooks only.

Prerequisite:
- Ensure project-root `.env` exists (`cp .env.example .env` or `Copy-Item .env.example .env`) before starting lab scripts.

Guidelines:
- Keep production transformations in `ingestion/` and `transformations/`.
- Use notebooks for ad-hoc analysis, profiling, and stakeholder-facing demos.
- Promote stable notebook logic into versioned Python modules when it becomes reusable.

Quick start in a new notebook:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("novalake_notebook").getOrCreate()

spark.sql("SHOW TABLES IN novalake.bronze").show(truncate=False)
spark.sql("SELECT * FROM novalake.gold.daily_revenue ORDER BY order_date").show()
```

Starter notebooks:
- `notebooks/01_lakehouse_exploration.ipynb`
- `notebooks/02_gold_validation.ipynb`
