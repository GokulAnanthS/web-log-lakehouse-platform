from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, sum as _sum
)

spark = SparkSession.builder.appName("GoldTrafficHourly").getOrCreate()

SILVER_PATH = "/app/lakehouse/silver/web_logs_parsed_parquet/success"
GOLD_PATH = "/app/lakehouse/gold/traffic_hourly"

silver = spark.read.parquet(SILVER_PATH)

gold_hourly = (
    silver
    .groupBy("event_date", "event_hour")
    .agg(
        count("*").alias("request_count"),
        countDistinct("client_ip").alias("unique_ips"),
        _sum(col("is_bot").cast("int")).alias("bot_requests"),
        _sum((col("status_code") >= 400).cast("int")).alias("error_requests")
    )
    .withColumn(
        "error_rate",
        col("error_requests") / col("request_count")
    )
)

(
    gold_hourly
    .write
    .mode("overwrite")
    .partitionBy("event_date")
    .parquet(GOLD_PATH)
)

spark.stop()
