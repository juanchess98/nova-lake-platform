"""Build payment success rate gold mart from silver payments and orders."""

from pyspark.sql import functions as F

from core.spark import create_spark_session, ensure_namespace, get_logger, table_identifier, write_iceberg_table


def main() -> None:
    logger = get_logger("novalake.jobs.transform.payment_success_rate_gold")
    spark = create_spark_session("novalake_payment_success_rate_gold")
    logger.info("Starting transform job: silver.payments -> gold.payment_success_rate")

    try:
        payments_df = spark.table(table_identifier("silver", "payments"))

        payment_success_df = (
            payments_df.withColumn("payment_date", F.to_date("payment_timestamp"))
            .groupBy("payment_date", "payment_method", "currency")
            .agg(
                F.count("payment_id").alias("attempt_count"),
                F.sum(F.when(F.col("payment_status") == "paid", 1).otherwise(0)).alias("success_count"),
                F.sum(F.when(F.col("payment_status") == "failed", 1).otherwise(0)).alias("failed_count"),
                F.sum(F.when(F.col("payment_status") == "pending", 1).otherwise(0)).alias("pending_count"),
                F.round(F.sum("payment_amount"), 2).alias("attempted_amount"),
            )
            .withColumn(
                "success_rate",
                F.round(F.col("success_count") / F.when(F.col("attempt_count") == 0, F.lit(1)).otherwise(F.col("attempt_count")), 4),
            )
            .withColumn("_processed_timestamp", F.current_timestamp())
        )

        ensure_namespace(spark, "gold")
        write_iceberg_table(payment_success_df, "gold", "payment_success_rate")
        logger.info("Completed transform job: wrote table novalake.gold.payment_success_rate")
    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
