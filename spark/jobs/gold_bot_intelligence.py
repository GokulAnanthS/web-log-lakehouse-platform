from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, avg
)

spark = SparkSession.builder.appName("GoldBotIntelligence").getOrCreate()

SILVER_PATH = "/app/lakehouse/silver/web_logs_parsed_parquet/success"
GOLD_PATH = "/app/lakehouse/gold/bot_intelligence"

silver = spark.read.parquet(SILVER_PATH).filter(col("is_bot") == True)

gold_bot = (
    silver
    .groupBy("event_date", "bot_name")
    .agg(
        count("*").alias("request_count"),
        countDistinct("client_ip").alias("unique_ips"),
        avg("event_hour").alias("avg_active_hour")
    )
)

(
    gold_bot
    .write
    .mode("overwrite")
    .partitionBy("event_date")
    .parquet(GOLD_PATH)
)
gold_bot.show(10,False)
spark.stop()
