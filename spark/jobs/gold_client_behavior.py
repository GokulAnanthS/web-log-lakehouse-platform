from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, sum as _sum
)

spark = SparkSession.builder.appName("GoldClientBehavior").getOrCreate()

SILVER_PATH = "/app/lakehouse/silver/web_logs_parsed_parquet/success"
GOLD_PATH = "/app/lakehouse/gold/client_behavior"

silver = spark.read.parquet(SILVER_PATH)

gold_client = (
    silver
    .groupBy("event_date", "client_ip", "device_type")
    .agg(
        count("*").alias("request_count"),
        countDistinct("uri_path_decoded").alias("unique_urls"),
        _sum((col("status_code") >= 400).cast("int")).alias("error_requests"),
        _sum(col("is_bot").cast("int")).alias("bot_requests")
    )
    .withColumn(
        "error_rate",
        col("error_requests") / col("request_count")
    )
)

(
    gold_client
    .write
    .mode("overwrite")
    .partitionBy("event_date")
    .parquet(GOLD_PATH)
)

spark.stop()
