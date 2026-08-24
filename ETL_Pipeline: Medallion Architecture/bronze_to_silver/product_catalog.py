from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name="retail_b.retail_silver.product_catalog",
    comment="Silver layer product catalog with standardization and data quality rules"
)
@dp.expect_or_drop("valid_product_id", "product_id IS NOT NULL AND LENGTH(TRIM(product_id)) > 0")
@dp.expect_or_drop("valid_product_name", "product_name IS NOT NULL AND LENGTH(TRIM(product_name)) > 0")
@dp.expect_or_drop("valid_price", "unit_price IS NOT NULL AND unit_price >= 0")
@dp.expect("valid_category", "category IS NOT NULL")
@dp.expect("valid_launch_date", "launch_date IS NULL OR launch_date <= CURRENT_DATE()")
@dp.expect("active_flag_set", "is_active IS NOT NULL")

def silver_product_catalog():
    """Silver layer product catalog with standardization operations."""
    return (
        spark.readStream
        .option("skipChangeCommits", "true")
        .table("retail_b.postgres_bronze.product_catalog")
        .select(
            # Standardize product_id: trim and uppercase
            F.upper(F.trim(F.col("product_id"))).alias("product_id"),
            
            # Standardize product_name: trim
            F.trim(F.col("product_name")).alias("product_name"),
            
            # Standardize category: trim and uppercase
            F.upper(F.trim(F.col("category"))).alias("category"),
            
            # Standardize subcategory: trim and uppercase
            F.upper(F.trim(F.col("subcategory"))).alias("subcategory"),
            
            # Standardize brand: trim
            F.trim(F.col("brand")).alias("brand"),
            
            # Keep unit_price as is (already decimal)
            F.col("unit_price"),
            
            # Standardize supplier_name: trim
            F.trim(F.col("supplier_name")).alias("supplier_name"),
            
            # Keep launch_date as is
            F.col("launch_date"),
            
            # Standardize is_active: coalesce to false if null
            F.coalesce(F.col("is_active"), F.lit(False)).alias("is_active"),
            
            # Keep updated_at timestamp
            F.col("updated_at"),

            # Derived column based on business logic
            F.when(F.col("unit_price")>50000,"PREMIUM").when(F.col("unit_price")>10000,"MID_RANGE").otherwise("BUDGET").alias("product_segment"),
            
            # Preserve SCD Type 2 tracking columns for full history
            F.col("__START_AT").alias("start_at"),
            F.col("__END_AT").alias("end_at"),
            
            # Add processing timestamp
            F.current_timestamp().alias("processed_at")
        )
    )