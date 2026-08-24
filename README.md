# Retail-Databricks-ETL-Pipeline

# Retail Data Pipeline — Databricks Lakehouse (Medallion Architecture)

End-to-end retail analytics pipeline built on Databricks, ingesting from PostgreSQL (NeonDB), Salesforce, and file-based storage, transformed through a Bronze → Silver → Gold medallion architecture, exposed via a governed semantic layer, and consumed through dashboards and a Genie natural-language agent.

---

## Architecture

```
┌─────────────┐   ┌──────────────┐   ┌────────────────┐
│  PostgreSQL │   │  Salesforce  │   │  File Storage   │
│  (NeonDB)   │   │  (CSV → SF)  │   │  (UC Volume)    │
└──────┬──────┘   └──────┬───────┘   └───────┬─────────┘
       │ Lakeflow        │ Lakeflow          │ Autoloader
       │ Connect         │ Connect           │ (PySpark)
       ▼                 ▼                   ▼
┌───────────────────────────────────────────────────────┐
│                     BRONZE LAYER                       │
│  postgres_bronze.*  salesforce_bronze.*  blob_bronze.transactions │
└───────────────────────────┬─────────────────────────────┘
                             │ Lakeflow Declarative Pipeline
                             ▼
┌───────────────────────────────────────────────────────┐
│                SILVER LAYER (retail_silver)             │
│  product_catalog · inventory · account · opportunities · transactions │
└───────────────────────────┬─────────────────────────────┘
                             ▼
┌───────────────────────────────────────────────────────┐
│                 GOLD LAYER (retail_gold)                │
│  dim_product · dim_customer · dim_calendar               │
│  fact_sales · fact_inventory (standalone)                │
└───────────────────────────┬─────────────────────────────┘
                             ▼
┌───────────────────────────────────────────────────────┐
│          SEMANTIC LAYER (retail_semantic)                │
│          Metric View: retail_metrics                     │
└───────────────────────────┬─────────────────────────────┘
                             ▼
               Dashboards  +  Genie Space (AI/BI)
```

**Catalog:** `retail_b` (Unity Catalog)
**Schemas:** `postgres_bronze`, `salesforce_bronze`, `blob_bronze`, `volumes_schema`, `retail_silver`, `retail_gold`, `retail_semantic`

---

## Data Sources & Ingestion

| Source | Method | Target (Bronze) | Load Type |
|---|---|---|---|
| PostgreSQL (NeonDB) — `inventory` (SCD1), `product_catalog` (SCD2) | Lakeflow Connect (Postgres connector) | `retail_b.postgres_bronze.*` | Incremental (CDC) |
| Salesforce — `Account`, `Opportunity` | Lakeflow Connect (Salesforce connector), history tracking enabled → auto SCD Type 2 | `retail_b.salesforce_bronze.*` | Incremental |
| Flat files (`transactions` CSV) | Unity Catalog managed Volume + Auto Loader (PySpark, notebook) | `retail_b.blob_bronze.transactions` | Incremental (file-based) |

Credentials for the PostgreSQL connection are stored in a Databricks secret scope / Unity Catalog connection object, not in code or notebooks.

Salesforce ingestion pulls in all default Salesforce objects, most of which are empty; only `Account` and `Opportunity` are selected for downstream use.

---

## Bronze → Silver Transformations

Built as a Lakeflow (Spark) Declarative Pipeline, one streaming table per source, with standardization and data quality checks applied per table.

| Silver Table | Source | Key Transformations |
|---|---|---|
| `product_catalog` | `postgres_bronze.product_catalog` | Filters to active rows only; derives `is_active` from whether `end_at` is null (current-record flag for SCD2); derives `product_segment` (`PREMIUM` / `MID_RANGE` / `BUDGET`) from `unit_price` |
| `inventory` | `postgres_bronze.inventory` | Derives `inventory_status` (`LOW_STOCK` / `HEALTHY`) by comparing `stock_quantity` to `reorder_level` |
| `account` | `salesforce_bronze.account` | Prunes Salesforce's default-null columns down to core business fields |
| `opportunities` | `salesforce_bronze.opportunity` | Prunes to necessary columns; derives `deal_size` (`ENTERPRISE` / `MID-MARKET` / `SMALL`) from `amount` |
| `transactions` | `blob_bronze.transactions` | Derives `gross_amount` = `selling_price * quantity` |

---

## Gold Layer — Star Schema

### Dimension Tables

Materialized as views over clean Silver tables — no physical duplication.

| Table | Source | Notes |
|---|---|---|
| `dim_product` | `retail_silver.product_catalog` | Filtered to `is_active = true` |
| `dim_customer` | `retail_silver.account` | Filtered to `is_deleted = false AND is_active = true` |
| `dim_calendar` | Generated in Databricks (no source system) | Date-keyed, standard year/month/week attributes, built for a configurable start/end date range |

### Fact Tables

| Table | Grain | Build | Notes |
|---|---|---|---|
| `fact_sales` | One row per transaction | Notebook, `silver_to_gold` pipeline stage | Central fact table. Left join of `transactions` (blob) to `opportunities` (Salesforce) on `opportunity_name = name` |
| `fact_inventory` | One row per inventory record | Notebook (run-once, not part of the recurring pipeline) | Not part of the star schema — used standalone for inventory analysis and dashboards |

---

## Semantic Layer — Metric Views

- Schema: `retail_b.retail_semantic`
- Metric View: `retail_metrics`, defined in YAML+SQL over `fact_sales`, `dim_product`, `dim_customer`, `dim_calendar`
- 12 measures, 26 dimensions, queryable via SQL or dashboards without needing a bespoke view per question.

---

## Consumption Layer

- **Databricks Dashboard** — built against `retail_semantic.retail_metrics`, refreshed as the final step of the orchestration job.
- **Genie Space** — pointed at the Gold layer tables (`dim_calendar`, `dim_customer`, `dim_product`, `fact_inventory`, `fact_sales`) for natural-language Q&A (AI/BI).

---

## Orchestration

Single Databricks Job (**Retail End-to-End**) chaining all layers:

```
postgres_to_bronze → salesforce_to_bronze → blob_to_bronze → silver_and_gold → dashboard_refresh
```

| Task | Type | Depends on |
|---|---|---|
| `postgres_to_bronze` | Ingestion pipeline | — |
| `salesforce_to_bronze` | Ingestion pipeline | `postgres_to_bronze` |
| `blob_to_bronze` | Notebook (serverless) | `salesforce_to_bronze` |
| `silver_and_gold` | Pipeline (`retail_transformations_v2`) | `blob_to_bronze` |
| `dashboard_refresh` | Dashboard task | `silver_and_gold` |

Trigger: manual, or schedule-based.

---

## Summary

- **Ingestion:** PostgreSQL, Salesforce, file-based, via Lakeflow Connect + Auto Loader (incremental)
- **Transformation:** Medallion architecture via Lakeflow Declarative Pipelines
- **Modeling:** Star schema (Gold layer) with SCD1/SCD2 handling
- **Semantics:** Governed metric view (12 measures, 26 dimensions)
- **Consumption:** Databricks Dashboard + Genie Space (AI/BI)
- **Orchestration:** Single end-to-end Databricks Job with dashboard refresh as final step
