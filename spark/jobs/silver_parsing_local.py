from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, regexp_extract, to_timestamp, when, lit,
    lower, hour, udf, regexp_replace, trim, length,expr
)
from pyspark.sql.types import StringType
from urllib.parse import unquote



spark = (
    SparkSession.builder
    .appName("SilverWebLogParsingLocal")
    .getOrCreate()
)

BRONZE_PATH = "/app/lakehouse/bronze/web_logs_parquet"
SILVER_PATH = "/app/lakehouse/silver/web_logs_parsed_parquet"

bronze = spark.read.parquet(BRONZE_PATH)
bronze.show(10,False)

LOG_PATTERN = (
    r'^(\d{1,3}(?:\.\d{1,3}){3})\s+\S+\s+\S+\s+\[([^\]]+)\]\s+'
    r'"(\S+)\s+([^\s?]+)(?:\?([^\s"]*))?\s+(HTTP\/[0-9.]+)"\s+'
    r'(\d{3})\s+(\S+)\s+"([^"]*)"\s+"([^"]*)"'
)

parsed = bronze.select(
    regexp_extract("raw_line", LOG_PATTERN, 1).alias("client_ip"),
    regexp_extract("raw_line", LOG_PATTERN, 2).alias("raw_timestamp"),
    regexp_extract("raw_line", LOG_PATTERN, 3).alias("http_method"),
    regexp_extract("raw_line", LOG_PATTERN, 4).alias("uri_path"),
    regexp_extract("raw_line", LOG_PATTERN, 5).alias("uri_query"),
    regexp_extract("raw_line", LOG_PATTERN, 6).alias("protocol"),
    regexp_extract("raw_line", LOG_PATTERN, 7).cast("int").alias("status_code"),
    regexp_extract("raw_line", LOG_PATTERN, 8).cast("long").alias("response_bytes"),
    regexp_extract("raw_line", LOG_PATTERN, 9).alias("referrer"),
    regexp_extract("raw_line", LOG_PATTERN, 10).alias("user_agent"),
    col("ingestion_time"),
    col("source_file")
)


silver = (
    parsed
    .withColumn(
        "event_timestamp",
        to_timestamp("raw_timestamp", "dd/MMM/yyyy:HH:mm:ss Z")
    )
    .withColumn(
        "parse_status",
        when(col("client_ip") == "", "failed").otherwise("success")
    )
    .withColumn(
        "event_date",
        col("event_timestamp").cast("date")
    )
    .withColumn(
        "event_hour",
        hour("event_timestamp")
    )
    .withColumn(
        "is_bot",
        lower(col("user_agent")).rlike("bot|crawler|spider")
    )
    .withColumn(
        "bot_name",
        when(lower(col("user_agent")).like("%ahrefs%"), "AhrefsBot")
        .when(lower(col("user_agent")).like("%bingbot%"), "BingBot")
        .when(lower(col("user_agent")).like("%googlebot%"), "GoogleBot")
        .otherwise(lit(None))
    )
    .withColumn(
        "device_type",
        when(col("is_bot"), "bot")
        .when(lower(col("user_agent")).rlike("mobile|android|iphone"), "mobile")
        .otherwise("desktop")
    )
)

silver = silver.withColumn(
    "uri_path_decoded",
    expr("url_decode(uri_path)")
).withColumn(
    "uri_query_decoded",
    expr("url_decode(uri_query)")
)


silver_success = silver.filter(col("parse_status") == "success")
silver_failed  = silver.filter(col("parse_status") == "failed")

silver_success.repartition("event_date").write.mode("overwrite").partitionBy("event_date").parquet(SILVER_PATH + "/success")
silver_failed.repartition("event_date").write.mode("overwrite").partitionBy("event_date").parquet(SILVER_PATH + "/failed")


spark.stop()