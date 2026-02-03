from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, avg, sum as _sum
)

spark = SparkSession.builder.appName("GoldURLPerformance").getOrCreate()

SILVER_PATH = "/app/lakehouse/silver/web_logs_parsed_parquet/success"
GOLD_PATH = "/app/lakehouse/gold/url_performance"

silver = spark.read.parquet(SILVER_PATH)

gold_url = (
    silver
    .groupBy("uri_path_decoded")
    .agg(
        count("*").alias("total_hits"),
        countDistinct("client_ip").alias("unique_ips"),
        avg("response_bytes").alias("avg_bytes"),
        _sum((col("status_code") >= 400).cast("int")).alias("error_hits"),
        _sum(col("is_bot").cast("int")).alias("bot_hits")
    )
    .withColumn(
        "error_rate",
        col("error_hits") / col("total_hits")
    )
    .withColumn(
        "bot_hit_ratio",
        col("bot_hits") / col("total_hits")
    )
)

(
    gold_url
    .write
    .mode("overwrite")
    .parquet(GOLD_PATH)
)

spark.stop()
