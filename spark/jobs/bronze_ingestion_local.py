from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit

spark = (
    SparkSession.builder
    .appName("BronzeWebLogIngestionLocal_UTF16")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .config("spark.sql.adaptive.enabled", "false")          # 🔑 CRITICAL
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)
# ------------------------------------------------------------------
# RAW LOG FILE (UTF-16 ENCODED)
# ------------------------------------------------------------------
RAW_PATH = "/app/data/sample/sample_access.log"
BRONZE_PATH = "/app/lakehouse/bronze/web_logs_delta"

# ------------------------------------------------------------------
# CORRECT READ STRATEGY
# ------------------------------------------------------------------
raw_df = (
    spark.read
    .format("csv")                 # Switch to CSV reader for better encoding support
    .option("encoding", "UTF-16")  # Tells Spark to consume the BOM correctly
    .option("sep", "\n")           # Force reading line-by-line
    .option("header", "false")     # Logs don't have CSV headers
    .load(RAW_PATH)
.withColumnRenamed("_c0", "raw_line")
)

raw_df.show(1, truncate=False)
bronze_df = (
    raw_df.withColumn("ingestion_time", current_timestamp()).withColumn("source_file", lit("sample_access.log"))
)

# bronze_df.show(1, truncate=False)
# Overwrite Bronze (intentional rebuild)
(
    bronze_df.write.format("delta").mode("overwrite").save(BRONZE_PATH)
)

bronze_df.show(5, truncate=False)

print("Bronze rebuilt successfully with UTF-16 encoding")

spark.stop()
