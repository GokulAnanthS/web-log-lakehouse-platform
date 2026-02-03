from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, sum as _sum, avg, when
)

spark = SparkSession.builder.appName("GoldTrafficDaily").getOrCreate()

SILVER_PATH = "/app/lakehouse/silver/web_logs_parsed_parquet/success"
GOLD_PATH = "/app/lakehouse/gold/traffic_daily"

silver = spark.read.parquet(SILVER_PATH)

gold_daily = (
    silver
    .groupBy("event_date")
    .agg(
        count("*").alias("total_requests"),
        countDistinct("client_ip").alias("unique_ips"),
        _sum(when(col("status_code").between(200, 299), 1).otherwise(0)).alias("success_requests"),
        _sum(when(col("status_code").between(400, 499), 1).otherwise(0)).alias("client_errors"),
        _sum(when(col("status_code").between(500, 599), 1).otherwise(0)).alias("server_errors"),
        _sum(when(col("is_bot"), 1).otherwise(0)).alias("bot_requests"),
        avg("response_bytes").alias("avg_response_bytes")
    )
    .withColumn(
        "bot_ratio",
        col("bot_requests") / col("total_requests")
    )
)

(
    gold_daily
    .write
    .mode("overwrite")
    .partitionBy("event_date")
    .parquet(GOLD_PATH)
)

spark.stop()
