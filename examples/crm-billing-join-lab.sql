-- Combined CRM + billing join lab
-- https://www.trycombined.com/resources/crm-billing-join-lab#deals=2&invoices=2
-- Synthetic, normalized teaching tables. Run this one statement in DuckDB.
-- Each deal is USD 10,000; each paid invoice is USD 2,500.
-- All invoices are in the sample's reporting window; this is invoice cash,
-- not MRR, ARR, recognized revenue, or a live product benchmark.
WITH
deals AS (
  SELECT 'deal_' || id AS deal_id, '101' AS company_id,
         'usd' AS currency, 10000.00 AS amount
  FROM range(1, 3) t(id)
),
invoices AS (
  SELECT 'invoice_' || id AS invoice_id, '101' AS company_id,
         'usd' AS currency, 2500.00 AS amount_paid
  FROM range(1, 3) t(id)
),
raw_join AS (
  SELECT d.company_id, d.currency, COUNT(*) AS rows_after_join,
         SUM(d.amount) AS pipeline, COALESCE(SUM(i.amount_paid), 0) AS paid
  FROM deals d
  LEFT JOIN invoices i USING (company_id, currency)
  GROUP BY d.company_id, d.currency
),
pipeline AS (
  SELECT company_id, currency, SUM(amount) AS pipeline
  FROM deals GROUP BY company_id, currency
),
billing AS (
  SELECT company_id, currency, SUM(amount_paid) AS paid
  FROM invoices GROUP BY company_id, currency
)
SELECT 'Raw join' AS method, company_id, currency,
       rows_after_join, pipeline, paid
FROM raw_join
UNION ALL
SELECT 'Aggregate first', p.company_id, p.currency,
       1 AS rows_after_join, p.pipeline, COALESCE(b.paid, 0) AS paid
FROM pipeline p
LEFT JOIN billing b USING (company_id, currency)
ORDER BY method DESC;
