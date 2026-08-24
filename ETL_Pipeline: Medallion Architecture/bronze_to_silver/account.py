from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name="retail_b.retail_silver.account",
    comment="Silver layer: Standardized Salesforce account data with data quality checks"
)
@dp.expect_or_drop("valid id", "Id IS NOT NULL")
@dp.expect("valid name", "customer_name IS NOT NULL")

def silver_account():
        #Read source streaming table 
        return (    
            spark.readStream.table("retail_b.salesforce_bronze.account")
            .select(
                # Core identifiers - trimmed
                F.trim(F.col("Id")).alias("id"),
                F.col("IsDeleted").alias("is_deleted"),
                
                # Basic information - trimmed and standardized
                F.trim(F.col("Name")).alias("customer_name"),
                F.upper(F.trim(F.col("Type"))).alias("type"),
                
                # Billing address - trimmed and standardized
                F.trim(F.col("BillingStreet")).alias("billing_street"),
                F.initcap(F.trim(F.col("BillingCity"))).alias("billing_city"),
                F.upper(F.trim(F.col("BillingState"))).alias("billing_state"),
                F.trim(F.col("BillingPostalCode")).alias("billing_postal_code"),
                F.upper(F.trim(F.col("BillingCountry"))).alias("billing_country"),
                
                # Shipping address - trimmed and standardized
                F.trim(F.col("ShippingStreet")).alias("shipping_street"),
                F.initcap(F.trim(F.col("ShippingCity"))).alias("shipping_city"),
                F.upper(F.trim(F.col("ShippingState"))).alias("shipping_state"),
                F.trim(F.col("ShippingPostalCode")).alias("shipping_postal_Code"),
                F.upper(F.trim(F.col("ShippingCountry"))).alias("shipping_country"),
                
                # Contact information - trimmed and lowercased for consistency
                F.trim(F.col("Phone")).alias("phone"),
                F.lower(F.trim(F.col("Website"))).alias("website"),
                
                # Company details - trimmed and standardized
                F.coalesce(F.col("Industry"),F.lit("UNKNOWN")).alias("industry"),
                F.col("NumberOfEmployees").alias("number_of_employees"),
                F.trim(F.col("Description")).alias("description"),
                
                
                # Compute is_active: true when __END_AT is null (active record). otherwise false
                F.when(F.col("__END_AT").isNull(), True).otherwise(False).alias("is_active")
               
        )
    )