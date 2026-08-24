SELECT
  product_id,
  product_name,
  category,
  subcategory,
  brand,
  product_segment,
  unit_price,
  supplier_name,
  launch_date,
  updated_at
FROM
  retail_b.retail_silver.product_catalog
where
  is_active = true
