# Databricks notebook source
# DBTITLE 1,Create Calendar Dimension Table
# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE retail_b.retail_gold.dim_calendar AS
# MAGIC WITH date_spine AS (
# MAGIC   SELECT explode(sequence(
# MAGIC     to_date(:start_date),
# MAGIC     to_date(:end_date),
# MAGIC     interval 1 day
# MAGIC   )) AS date
# MAGIC )
# MAGIC SELECT 
# MAGIC   date,
# MAGIC   -- Year attributes
# MAGIC   year(date) AS year,
# MAGIC   quarter(date) AS quarter,
# MAGIC   
# MAGIC   -- Month attributes
# MAGIC   month(date) AS month,
# MAGIC   date_format(date, 'MMMM') AS month_name,
# MAGIC   date_format(date, 'MMM') AS month_short_name,
# MAGIC   concat(year(date), '-', lpad(month(date), 2, '0')) AS year_month,
# MAGIC   
# MAGIC   -- Week attributes
# MAGIC   weekofyear(date) AS week_of_year,
# MAGIC   date_trunc('week', date) AS week_start_date,
# MAGIC   
# MAGIC   -- Day attributes
# MAGIC   dayofmonth(date) AS day_of_month,
# MAGIC   dayofyear(date) AS day_of_year,
# MAGIC   dayofweek(date) AS day_of_week,  -- 1=Sunday, 7=Saturday
# MAGIC   date_format(date, 'EEEE') AS day_name,
# MAGIC   date_format(date, 'EEE') AS day_short_name,
# MAGIC   
# MAGIC   -- Business day indicators
# MAGIC   CASE WHEN dayofweek(date) IN (1, 7) THEN false ELSE true END AS is_weekday,
# MAGIC   CASE WHEN dayofweek(date) IN (1, 7) THEN true ELSE false END AS is_weekend,
# MAGIC   
# MAGIC   -- First/Last day flags
# MAGIC   CASE WHEN dayofmonth(date) = 1 THEN true ELSE false END AS is_first_day_of_month,
# MAGIC   CASE WHEN date = last_day(date) THEN true ELSE false END AS is_last_day_of_month,
# MAGIC   CASE WHEN dayofyear(date) = 1 THEN true ELSE false END AS is_first_day_of_year,
# MAGIC   CASE WHEN month(date) = 12 AND dayofmonth(date) = 31 THEN true ELSE false END AS is_last_day_of_year,
# MAGIC   
# MAGIC   -- Date string formats (useful for display)
# MAGIC   date_format(date, 'yyyy-MM-dd') AS date_iso,
# MAGIC   date_format(date, 'dd/MM/yyyy') AS date_us_format,
# MAGIC   
# MAGIC   -- Quarter year
# MAGIC   concat('Q', quarter(date), ' ', year(date)) AS quarter_year
# MAGIC   
# MAGIC FROM date_spine
# MAGIC ORDER BY date;

# COMMAND ----------

# DBTITLE 1,Verify Calendar Table
# MAGIC %sql
# MAGIC -- Display a sample of the calendar table
# MAGIC SELECT * FROM retail_b.retail_gold.calendar LIMIT 10