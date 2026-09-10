-- Synthetic Salesforce + Chargebee teaching example; read-only DuckDB SQL.
-- Snapshot: 2026-09-10 00:00 UTC. Upcoming term ends: [2026-09-10, 2026-10-10).
-- Normalized aliases below are not actual Combined dataset names.
-- Expected: Atlas/USD/2 terms/0 nonrenewing/1 overdue invoice/500.00 due;
--           Birch/USD/1 term/1 nonrenewing/0 overdue invoices/0.00 due.
WITH
accounts(account_id, account_name) AS (VALUES ('a1','Atlas'),('a2','Birch'),('a3','Cedar')),
customer_map(account_id, customer_id) AS (VALUES ('a1','cb1'),('a2','cb2'),('a3','cb3')),
subscriptions(subscription_id, customer_id, currency, status, term_end) AS (VALUES
  ('s1','cb1','USD','active',TIMESTAMP '2026-09-15'),
  ('s2','cb1','USD','active',TIMESTAMP '2026-09-25'),
  ('s3','cb2','USD','non_renewing',TIMESTAMP '2026-09-20'),
  ('s4','cb3','USD','cancelled',TIMESTAMP '2026-09-15'),
  ('s5','cb1','USD','active',TIMESTAMP '2026-10-10')),
invoices(invoice_id, customer_id, currency, status, due_at, amount_due_minor) AS (VALUES
  ('i1','cb1','USD','payment_due',TIMESTAMP '2026-09-01',50000),
  ('i2','cb1','USD','payment_due',TIMESTAMP '2026-09-20',80000),
  ('i3','cb1','USD','paid',TIMESTAMP '2026-09-01',0),
  ('i4','cb2','USD','payment_due',TIMESTAMP '2026-09-10',12000),
  ('i5','cb3','USD','not_paid',TIMESTAMP '2026-09-01',35000)),
upcoming AS (
  SELECT m.account_id, s.currency, COUNT(*) AS upcoming_terms,
         SUM(CASE WHEN s.status='non_renewing' THEN 1 ELSE 0 END) AS nonrenewing_terms
  FROM subscriptions s JOIN customer_map m USING (customer_id)
  WHERE s.status IN ('active','non_renewing')
    AND s.term_end >= TIMESTAMP '2026-09-10'
    AND s.term_end < TIMESTAMP '2026-10-10'
  GROUP BY m.account_id,s.currency
), overdue AS (
  SELECT m.account_id,i.currency,COUNT(*) AS overdue_invoices,
         SUM(i.amount_due_minor)/100.0 AS overdue_balance
  FROM invoices i JOIN customer_map m USING (customer_id)
  WHERE i.status IN ('payment_due','not_paid') AND i.amount_due_minor>0
    AND i.due_at < TIMESTAMP '2026-09-10'
  GROUP BY m.account_id,i.currency
)
SELECT a.account_name,u.currency,u.upcoming_terms,u.nonrenewing_terms,
       COALESCE(o.overdue_invoices,0) AS overdue_invoices,
       COALESCE(o.overdue_balance,0) AS overdue_balance
FROM upcoming u JOIN accounts a USING (account_id)
LEFT JOIN overdue o ON o.account_id=u.account_id AND o.currency=u.currency
ORDER BY a.account_name,u.currency;
