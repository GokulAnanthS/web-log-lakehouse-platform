from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit

# Create Spark session with Delta support
spark = (
    SparkSession.builder
    .appName("BronzeWebLogIngestionLocal")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate()
)

# Paths (LOCAL)
RAW_PATH = "/app/data/sample/sample_access.log"
BRONZE_PATH = "/app/lakehouse/bronze/web_logs_delta"

# Read raw log file line-by-line (memory safe)
raw_df = spark.read.text(RAW_PATH)

bronze_df = (
    raw_df
    .withColumnRenamed("value", "raw_line")
    .withColumn("ingestion_time", current_timestamp())
    .withColumn("source_file", lit("sample_access.log"))
)

# Write Delta Bronze table
(
    bronze_df
    .write
    .format("delta")
    .mode("overwrite")
    .save(BRONZE_PATH)
)

print("Bronze Delta table created successfully at:", BRONZE_PATH)

spark.stop()
