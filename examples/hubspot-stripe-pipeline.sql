-- Combined: HubSpot + Stripe pipeline and paid-invoice example.
-- https://www.trycombined.com/resources/query-hubspot-and-stripe-with-ai
-- Synthetic normalized data; these are not connector relation names.
-- Run in DuckDB. This is one read-only statement and makes no network requests.
-- USD and EUR only: amount_paid_minor / 100 converts this fixture's minor units.
-- The interval is [2026-06-12, 2026-09-10), measured on paid_at, in UTC.
-- Invoice amount paid is not net-of-refund revenue, MRR or ARR.
WITH
companies(company_id, company_name) AS (
  VALUES ('101', 'Atlas'), ('102', 'Birch'), ('103', 'Cedar')
),
customer_map(stripe_customer_id, company_id) AS (
  VALUES ('cus_atlas', '101'), ('cus_birch', '102'), ('cus_cedar', '103')
),
deals(deal_id, company_id, currency, is_closed, amount) AS (
  VALUES
    ('deal_1', '101', 'usd', false, 12000.00),
    ('deal_2', '101', 'usd', false, 8000.00),
    ('deal_3', '102', 'usd', false, 6000.00),
    ('deal_4', '103', 'eur', false, 4000.00),
    ('deal_5', '101', 'usd', true, 5000.00),
    ('deal_6', '102', 'usd', true, 3000.00)
),
invoices(invoice_id, stripe_customer_id, currency, status, amount_paid_minor, paid_at) AS (
  VALUES
    ('invoice_1', 'cus_atlas', 'usd', 'paid', 300000, TIMESTAMP '2026-07-15 12:00:00'),
    ('invoice_2', 'cus_atlas', 'usd', 'paid', 200000, TIMESTAMP '2026-08-10 12:00:00'),
    ('invoice_3', 'cus_birch', 'usd', 'open', 0, NULL),
    ('invoice_4', 'cus_birch', 'usd', 'paid', 100000, TIMESTAMP '2026-06-01 12:00:00'),
    ('invoice_5', 'cus_cedar', 'eur', 'paid', 150000, TIMESTAMP '2026-08-05 12:00:00'),
    ('invoice_6', 'cus_atlas', 'usd', 'void', 0, NULL)
),
open_pipeline AS (
  SELECT company_id, currency, COUNT(*) AS open_deals,
         SUM(amount) AS open_pipeline_amount
  FROM deals
  WHERE is_closed = false
  GROUP BY company_id, currency
),
paid_invoices AS (
  SELECT m.company_id, i.currency, COUNT(*) AS paid_invoice_count,
         SUM(i.amount_paid_minor) / 100.0 AS paid_invoice_amount
  FROM invoices i
  JOIN customer_map m USING (stripe_customer_id)
  WHERE i.status = 'paid'
    AND i.paid_at >= TIMESTAMP '2026-06-12 00:00:00'
    AND i.paid_at < TIMESTAMP '2026-09-10 00:00:00'
  GROUP BY m.company_id, i.currency
)
SELECT c.company_name, p.currency, p.open_deals, p.open_pipeline_amount,
       b.paid_invoice_count, b.paid_invoice_amount
FROM open_pipeline p
JOIN companies c USING (company_id)
LEFT JOIN paid_invoices b
  ON p.company_id = b.company_id AND p.currency = b.currency
ORDER BY c.company_name, p.currency
LIMIT 20;

-- Expected rows:
-- Atlas | usd | 2 | 20000.00 | 2    | 5000.00
-- Birch | usd | 1 |  6000.00 | NULL | NULL
-- Cedar | eur | 1 |  4000.00 | 1    | 1500.00
-- NULL means no matching paid invoice in this fixture's interval/currency.
-- Never equate it with proven zero activity when real-source coverage is unknown.
