from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name="retail_b.retail_silver.transactions",
    comment="Cleaned and standardized transaction data with proper data types"
)
@dp.expect_or_drop("valid_transaction_id", "transaction_id IS NOT NULL AND TRIM(transaction_id) != ''")
@dp.expect_or_drop("valid_product_id", "product_id IS NOT NULL AND TRIM(product_id) != ''")
@dp.expect_or_drop("valid_store_id", "store_id IS NOT NULL AND TRIM(store_id) != ''")
@dp.expect("valid_quantity", "quantity > 0")
@dp.expect("valid_selling_price", "selling_price >= 0")
@dp.expect("valid_discount", "discount_amount >= 0")
@dp.expect("valid payment_mode", "payment_mode IN ('UFI','card', 'cash', 'Not Banking')")

def transactions_clean():
    return (
        spark.readStream.table("retail_b.blob_bronze.transactions")
        .select(
            # Core identifiers - trimmed and standardized
            F.upper(F.trim(F.col("transaction_id"))).alias("transaction_id"),
            F.trim(F.col("opportunity_name")).alias("opportunity_name"),
            F.upper(F.trim(F.col("product_id"))).alias("product_id"),
            F.upper(F.trim(F.col("store_id"))).alias("store_id"),
            
            # Numeric fields - cast from string to proper types
            F.col("quantity").cast("int").alias("quantity"),
            F.col("selling_price").cast("int").alias("selling_price"),

            # Derived calculated fields for gross amount
            (F.col("selling_price").cast("int") * F.col("quantity").cast("int")).alias("gross_amount"),
            
            F.col("discount_amount").cast("int").alias("discount_amount"),

            # Parse timestamp from string format "21-Apr-2026 07.35.51 AM"
            F.to_timestamp(
                F.col("transaction_timestamp"),
                "dd-MMM-yyyy hh.mm.ss a"
            ).alias("transaction_timestamp"),
            
            # Categorical fields - trimmed and standardized
            F.upper(F.trim(F.col("payment_mode"))).alias("payment_mode"),
            F.upper(F.trim(F.col("sales_channel"))).alias("sales_channel") 
        )
    )