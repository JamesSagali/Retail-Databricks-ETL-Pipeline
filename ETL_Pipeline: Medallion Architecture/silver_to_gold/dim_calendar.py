%sql
CREATE OR REPLACE TABLE retail_b.retail_gold.dim_calendar AS
WITH date_spine AS (
  SELECT explode(sequence(
    to_date(:start_date),
    to_date(:end_date),
    interval 1 day
  )) AS date
)
SELECT 
  date,
  -- Year attributes
  year(date) AS year,
  quarter(date) AS quarter,
  
  -- Month attributes
  month(date) AS month,
  date_format(date, 'MMMM') AS month_name,
  date_format(date, 'MMM') AS month_short_name,
  concat(year(date), '-', lpad(month(date), 2, '0')) AS year_month,
  
  -- Week attributes
  weekofyear(date) AS week_of_year,
  date_trunc('week', date) AS week_start_date,
  
  -- Day attributes
  dayofmonth(date) AS day_of_month,
  dayofyear(date) AS day_of_year,
  dayofweek(date) AS day_of_week,  -- 1=Sunday, 7=Saturday
  date_format(date, 'EEEE') AS day_name,
  date_format(date, 'EEE') AS day_short_name,
  
  -- Business day indicators
  CASE WHEN dayofweek(date) IN (1, 7) THEN false ELSE true END AS is_weekday,
  CASE WHEN dayofweek(date) IN (1, 7) THEN true ELSE false END AS is_weekend,
  
  -- First/Last day flags
  CASE WHEN dayofmonth(date) = 1 THEN true ELSE false END AS is_first_day_of_month,
  CASE WHEN date = last_day(date) THEN true ELSE false END AS is_last_day_of_month,
  CASE WHEN dayofyear(date) = 1 THEN true ELSE false END AS is_first_day_of_year,
  CASE WHEN month(date) = 12 AND dayofmonth(date) = 31 THEN true ELSE false END AS is_last_day_of_year,
  
  -- Date string formats (useful for display)
  date_format(date, 'yyyy-MM-dd') AS date_iso,
  date_format(date, 'dd/MM/yyyy') AS date_us_format,
  
  -- Quarter year
  concat('Q', quarter(date), ' ', year(date)) AS quarter_year
  
FROM date_spine
ORDER BY date;
