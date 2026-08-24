from pyspark.sql.functions import upper, trim, sum as _sum, countDistinct, col
from pyspark import pipelines as dp

@dp.table(name="retail_b.retail_gold.fact_sales")
def fact_sales():
    # Reading the tables that will be joined to form the fact table: transactions and opportunities silver tables
    transactions_df = spark.read.table("retail_b.retail_silver.transactions")
    opportunities_df = spark.read.table("retail_b.retail_silver.opportunities")

    # Joining the tables
    joined_df = transactions_df.alias("t").join(
        opportunities_df.alias("o"),
        upper(trim(transactions_df.opportunity_name)) == upper(trim(opportunities_df.name)),
        how="left"
    )

    # Selecting required columns for the fact table
    selected_df = joined_df.select(
        "t.transaction_id",
        "t.opportunity_name",
        "t.product_id",
        "t.store_id",
        "t.quantity",
        "t.selling_price",
        "t.discount_amount",
        "t.transaction_timestamp",
        # Derived column for date. Will help in joining with the dim_calender table
        col("t.transaction_timestamp").cast("date").alias("transaction_date"),
        "t.payment_mode",
        "t.sales_channel",
        "o.name",
        "o.stage_name",
        "o.owner_id",
        "o.amount",
        col("o.account_id").alias("customer_id")
    )

    return selected_df
  