from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name="retail_b.retail_silver.opportunities",
    comment="Cleaned and standardized opportunity data from Salesforce"
)
@dp.expect_or_drop("valid_id", "id IS NOT NULL")
@dp.expect("valid_name", "name IS NOT NULL AND TRIM(name) != ''")
@dp.expect("valid_stage_name", "stage_name IN ('Prospecting','Closed Won', 'Closed Lost')")
@dp.expect("valid_amount", "amount IS NULL OR amount >= 0")
@dp.expect("valid_probability", "probability IS NULL OR (probability >= 0 AND probability <= 100)")

def opportunities():
    return (
        spark.readStream.table("retail_b.salesforce_bronze.opportunity")
        .select(
            # Primary identifiers
            F.col("Id").alias("id"),
            F.col("IsDeleted").alias("is_deleted"),
            F.col("AccountId").alias("account_id"),
            
            # Core opportunity details
            F.trim(F.col("Name")).alias("name"),
            F.trim(F.col("Description")).alias("description"),
            F.trim(F.col("StageName")).alias("stage_name"),
            F.col("Amount").alias("amount"),

            # Derived fields for the deal classification
            F.when(F.col("amount") >100000, "ENTERPRISE")
                .when(F.col("amount") >25000, "MID-MARKET")
                .otherwise("SMALL")
                .alias("deal_size"),

            F.col("Probability").alias("probability"),
            F.col("CloseDate").alias("close_date"),
            F.col("OwnerId").alias("owner_id"),
            
            # Opportunity classification
            F.trim(F.col("Type")).alias("type"),
            F.trim(F.col("LeadSource")).alias("lead_source"),
            F.trim(F.col("ForecastCategory")).alias("forecast_category"),
            
            # Status flags
            F.col("IsClosed").alias("is_closed"),
            F.col("IsWon").alias("is_won"),
            
            # Additional context
            F.trim(F.col("NextStep")).alias("next_step"),
            F.col("CampaignId").alias("campaign_id"),
            F.col("CreatedDate").alias("created_date"),
            F.col("LastModifiedDate").alias("last_modified_date")
        )
    )