from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, regexp_extract, to_timestamp, lit,
    when, current_timestamp, input_file_name,
    year, month, dayofmonth, hour,regexp_replace, split, lower, udf, col
)

from urllib.parse import unquote
from pyspark.sql.types import StringType
from pyspark.sql.functions import udf

@udf(returnType=StringType())
def url_decode(value):
    if value is None:
        return None
    try:
        return unquote(value)
    except Exception:
        return value

spark = (
    SparkSession.builder
    .appName("SilverWebLogParsingLocal")
    .getOrCreate()
)


BRONZE_PATH = "/app/lakehouse/bronze/web_logs_delta"

log_pattern = r'^(\S+)\s+\S+\s+\S+\s+\[([^\]]+)\]\s+"(\S+)\s+(.+?)\s+(HTTP\/[0-9.]+)"\s+(\d{3})\s+(\S+)\s+"([^"]*)"\s+"([^"]*)"\s*"([^"]*)"?'



df = (
    spark.read
    .format("csv")
    .option("encoding", "UTF-16")      # This fixes the ?? characters
    .option("header", "false")
    .option("sep", "\n")               # Reads line-by-line
    .load("/app/data/sample/sample_access.log")
    .withColumnRenamed("_c0", "raw_line")
)

df.select("raw_line").show(2, truncate=False)


df = df.withColumn("ingestion_time", current_timestamp()) \
       .withColumn("source_file", lit("sample_access.log"))



parsed = df.select(
    regexp_extract("raw_line", log_pattern, 1).alias("client_ip"),
    regexp_extract("raw_line", log_pattern, 2).alias("raw_timestamp"),
    regexp_extract("raw_line", log_pattern, 3).alias("http_method"),
    regexp_extract("raw_line", log_pattern, 4).alias("uri_path"),
    lit(None).alias("uri_query"),
    regexp_extract("raw_line", log_pattern, 5).alias("protocol"),
    regexp_extract("raw_line", log_pattern, 6).cast("int").alias("status_code"),
    regexp_extract("raw_line", log_pattern, 7).cast("long").alias("response_bytes"),
    regexp_extract("raw_line", log_pattern, 8).alias("referrer"),
    regexp_extract("raw_line", log_pattern, 9).alias("user_agent"),
    col("ingestion_time") if "ingestion_time" in df.columns else lit(None).alias("ingestion_time"),
    col("source_file") if "source_file" in df.columns else lit("local_sample").alias("source_file")
)


parsed = parsed.withColumn(
    "event_timestamp",
    to_timestamp("raw_timestamp", "dd/MMM/yyyy:HH:mm:ss Z")
)

parsed = parsed.withColumn(
    "parse_status",
    when(col("client_ip") == "", lit("failed")).otherwise(lit("success"))
)

parsed = parsed.withColumn(
    "parse_error",
    when(col("parse_status") == "failed", lit("regex_no_match")).otherwise(lit(None))
)

parsed = parsed.withColumn("event_date", col("event_timestamp").cast("date")) \
               .withColumn("event_hour", hour("event_timestamp"))

parsed = parsed.withColumn(
    "uri_path_only",
    split(col("uri_path"), "\\?").getItem(0)
).withColumn(
    "uri_query",
    split(col("uri_path"), "\\?").getItem(1)
)

parsed = parsed.withColumn(
    "uri_path_decoded",
    url_decode(col("uri_path_only"))
).withColumn(
    "uri_query_decoded",
    url_decode(col("uri_query"))
)

parsed = parsed.withColumn(
    "is_bot",
    lower(col("user_agent")).rlike("bot|crawler|spider")
)

parsed = parsed.withColumn(
    "bot_name",
    when(lower(col("user_agent")).like("%ahrefs%"), "AhrefsBot")
    .when(lower(col("user_agent")).like("%bingbot%"), "BingBot")
    .when(lower(col("user_agent")).like("%googlebot%"), "GoogleBot")
    .otherwise(None)
)

parsed = parsed.withColumn(
    "device_type",
    when(col("is_bot") == True, "bot")
    .when(lower(col("user_agent")).like("%mobile%"), "mobile")
    .when(lower(col("user_agent")).like("%android%"), "mobile")
    .when(lower(col("user_agent")).like("%iphone%"), "mobile")
    .otherwise("desktop")
)
parsed.select(
    "client_ip",
    "event_timestamp",
    "http_method",
    "uri_path",
    "uri_path_decoded",
    "uri_query_decoded",
    "status_code",
    "user_agent",
    "is_bot",
    "bot_name",
    "device_type",
    "parse_status"
).show(5, truncate=False)


spark.stop()
