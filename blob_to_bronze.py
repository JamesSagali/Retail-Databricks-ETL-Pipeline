# Databricks notebook source
# DBTITLE 1,Auto Loader: CSV to Bronze
# Auto Loader ingestion from Volume to Bronze table
from pyspark.sql.functions import current_timestamp

# Source and target configuration
source_path = "/Volumes/retail_b/volumes_schema/blob_source/transactions_source/"
target_table = "retail_b.blob_bronze.transactions"

# Read CSV files using Auto Loader
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("header", "true")
  .option("inferSchema", "true")
  .option("cloudFiles.schemaLocation", "/Volumes/retail_b/volumes_schema/blob_source/_schema/transactions")
  .load(source_path)
  .withColumn("ingestion_timestamp", current_timestamp())
)

# Write to bronze table
(df.writeStream
  .format("delta")
  .option("checkpointLocation", "/Volumes/retail_b/volumes_schema/blob_source/_checkpoint/transactions")
  .option("mergeSchema", "true")
  .trigger(availableNow=True)
  .toTable(target_table)
)