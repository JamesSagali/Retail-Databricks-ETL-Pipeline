# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW retail_b.retail_semantic.retail_metrics
# MAGIC WITH METRICS
# MAGIC LANGUAGE YAML
# MAGIC AS $$
# MAGIC version: 1.1
# MAGIC source: retail_b.retail_gold.fact_sales
# MAGIC comment: Retail metrics for sales performance and product analysis
# MAGIC joins:
# MAGIC   - name: products
# MAGIC     source: retail_b.retail_gold.dim_product
# MAGIC     on: source.product_id = products.product_id
# MAGIC   - name: calendar
# MAGIC     source: retail_b.retail_gold.dim_calendar
# MAGIC     on: source.transaction_date = calendar.date
# MAGIC   - name: customers
# MAGIC     source: retail_b.retail_gold.dim_customer
# MAGIC     on: source.customer_id = customers.customer_id
# MAGIC dimensions:
# MAGIC   - name: Product Category
# MAGIC     expr: products.category
# MAGIC     display_name: Product Category
# MAGIC     comment: Product category from dimension table
# MAGIC   - name: Product Brand
# MAGIC     expr: products.brand
# MAGIC     display_name: Product Brand
# MAGIC     comment: Brand of the product
# MAGIC   - name: Sales Channel
# MAGIC     expr: source.sales_channel
# MAGIC     display_name: Sales Channel
# MAGIC     comment: Channel through which sale was made
# MAGIC   - name: Year
# MAGIC     expr: calendar.year
# MAGIC     display_name: Year
# MAGIC     comment: Year of transaction
# MAGIC   - name: Quarter
# MAGIC     expr: calendar.quarter
# MAGIC     display_name: Quarter
# MAGIC     comment: Quarter of transaction
# MAGIC   - name: Customer Name
# MAGIC     expr: customers.customer_name
# MAGIC     display_name: Customer Name
# MAGIC     comment: Name of the customer
# MAGIC   - name: Customer Type
# MAGIC     expr: customers.customer_type
# MAGIC     display_name: Customer Type
# MAGIC     comment: Type or segment of customer
# MAGIC   - name: Billing City
# MAGIC     expr: customers.billing_city
# MAGIC     display_name: Billing City
# MAGIC     comment: Customer's billing city
# MAGIC   - name: Billing State
# MAGIC     expr: customers.billing_state
# MAGIC     display_name: Billing State
# MAGIC     comment: Customer's billing state
# MAGIC   - name: Billing Country
# MAGIC     expr: customers.billing_country
# MAGIC     display_name: Billing Country
# MAGIC     comment: Customer's billing country
# MAGIC   - name: Industry
# MAGIC     expr: customers.industry
# MAGIC     display_name: Industry
# MAGIC     comment: Customer's industry sector
# MAGIC measures:
# MAGIC   - name: Total Revenue
# MAGIC     expr: SUM(amount)
# MAGIC     display_name: Total Revenue
# MAGIC     comment: Sum of all sales amounts
# MAGIC     format:
# MAGIC       type: currency
# MAGIC       currency_code: USD
# MAGIC       decimal_places:
# MAGIC         type: exact
# MAGIC         places: 2
# MAGIC   - name: Total Quantity
# MAGIC     expr: SUM(quantity)
# MAGIC     display_name: Total Quantity
# MAGIC     comment: Total units sold
# MAGIC     format:
# MAGIC       type: number
# MAGIC       decimal_places:
# MAGIC         type: exact
# MAGIC         places: 0
# MAGIC   - name: Transaction Count
# MAGIC     expr: COUNT(1)
# MAGIC     display_name: Transaction Count
# MAGIC     comment: Number of transactions
# MAGIC   - name: Average Order Value
# MAGIC     expr: AVG(amount)
# MAGIC     display_name: Average Order Value
# MAGIC     comment: Average transaction amount
# MAGIC     format:
# MAGIC       type: currency
# MAGIC       currency_code: USD
# MAGIC       decimal_places:
# MAGIC         type: exact
# MAGIC         places: 2
# MAGIC   - name: Total Discount
# MAGIC     expr: SUM(discount_amount)
# MAGIC     display_name: Total Discount
# MAGIC     comment: Total discount amount given
# MAGIC     format:
# MAGIC       type: currency
# MAGIC       currency_code: USD
# MAGIC       decimal_places:
# MAGIC         type: exact
# MAGIC         places: 2
# MAGIC   - name: Unique Customers
# MAGIC     expr: COUNT(DISTINCT source.customer_id)
# MAGIC     display_name: Unique Customers
# MAGIC     comment: Number of distinct customers
# MAGIC     format:
# MAGIC       type: number
# MAGIC       decimal_places:
# MAGIC         type: exact
# MAGIC         places: 0
# MAGIC $$