SELECT
  id as customer_id,
  customer_name,
  type as customer_type,
  billing_city,
  billing_state,
  billing_country,
  phone,
  website,
  industry,
  number_of_employees,
  description
FROM
  retail_b.retail_silver.account
WHERE
  is_deleted = false
  and is_active = true
