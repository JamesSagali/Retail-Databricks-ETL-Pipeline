# Databricks notebook source
# MAGIC %sql
# MAGIC
# MAGIC CREATE OR REPLACE VIEW retail_b.retail_gold.dim_customer AS
# MAGIC
# MAGIC SELECT  
# MAGIC     id as customer_id,
# MAGIC     customer_name,
# MAGIC     type as customer_type,
# MAGIC
# MAGIC     billing_city,
# MAGIC     billing_state,
# MAGIC     billing_country,
# MAGIC
# MAGIC     phone,
# MAGIC     website,
# MAGIC
# MAGIC     industry,
# MAGIC     number_of_employees,
# MAGIC
# MAGIC     description
# MAGIC
# MAGIC     FROM retail_b.retail_silver.account
# MAGIC     WHERE is_deleted = false and is_active = true;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC CREATE OR REPLACE VIEW retail_b.retail_gold.dim_product AS
# MAGIC
# MAGIC SELECT  
# MAGIC     product_id,
# MAGIC     product_name,
# MAGIC     category,
# MAGIC     subcategory,
# MAGIC     brand,
# MAGIC     product_segment,
# MAGIC     unit_price,
# MAGIC     supplier_name,
# MAGIC     launch_date,
# MAGIC     updated_at
# MAGIC
# MAGIC     FROM retail_b.retail_silver.product_catalog
# MAGIC     where is_active = true;  
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC CREATE OR REPLACE VIEW retail_b.retail_gold.fact_inventory AS
# MAGIC
# MAGIC SELECT  
# MAGIC     inventory_id,
# MAGIC     product_id,
# MAGIC     stock_quantity,
# MAGIC     reorder_level,
# MAGIC     inventory_status,
# MAGIC     warehouse_location,
# MAGIC     last_stock_update
# MAGIC
# MAGIC     FROM retail_b.retail_silver.inventory;
# MAGIC     
# MAGIC
# MAGIC