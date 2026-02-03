from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit

spark =     SparkSession.builder.appName("BronzeWebLogIngestionLocal").getOrCreate()

RAW_PATH = "/app/data/sample/access.log"
BRONZE_PATH = "/app/lakehouse/bronze/web_logs_parquet"

raw_df = spark.read.text(RAW_PATH).limit(50000)

bronze_df = (
    raw_df.withColumn("ingestion_time", current_timestamp())
    .withColumn("source_file", lit("sample_access.log"))
    .withColumnRenamed("value", "raw_line")   
)

bronze_df.show(10,False)

bronze_df.write.mode("overwrite").parquet(BRONZE_PATH)

print("Bronze Parquet table created successfully at:", BRONZE_PATH)

spark.stop()