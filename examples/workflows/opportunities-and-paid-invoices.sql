-- Synthetic Salesforce + Stripe teaching example; read-only DuckDB SQL.
-- Current open pipeline; paid invoices in [Jun 12, Sep 10), 2026 UTC.
-- Outstanding balance is current open invoices; undated collection is separate from overdue.
-- USD only. Expected Atlas: 20000 pipeline, 3000 paid, 700 outstanding,
-- 500 overdue, 200 undated. Birch: 6000 pipeline and zero billing amounts.
WITH
accounts(account_id,account_name) AS (VALUES ('a1','Atlas'),('a2','Birch'),('a3','Cedar')),
customer_map(account_id,customer_id) AS (VALUES ('a1','cus1'),('a2','cus2'),('a3','cus3')),
opportunities(opportunity_id,account_id,is_closed,amount,currency) AS (VALUES
 ('o1','a1',false,12000.00,'USD'),('o2','a1',false,8000.00,'USD'),
 ('o3','a2',false,6000.00,'USD'),('o4','a3',true,9000.00,'USD')),
invoices(invoice_id,customer_id,status,currency,amount_paid_minor,remaining_minor,paid_at,due_at) AS (VALUES
 ('i1','cus1','paid','USD',300000,0,TIMESTAMP '2026-09-01',NULL),
 ('i2','cus1','open','USD',50000,50000,NULL,TIMESTAMP '2026-09-01'),
 ('i3','cus1','open','USD',0,20000,NULL,NULL),
 ('i4','cus1','void','USD',0,100000,NULL,TIMESTAMP '2026-09-01'),
 ('i5','cus1','paid','USD',900000,0,TIMESTAMP '2026-06-11',NULL)),
pipeline AS (
 SELECT account_id,SUM(amount) AS open_pipeline
 FROM opportunities WHERE NOT is_closed AND currency='USD' GROUP BY account_id
), billing AS (
 SELECT m.account_id,
 SUM(CASE WHEN i.status='paid' AND i.paid_at>=TIMESTAMP '2026-06-12'
   AND i.paid_at<TIMESTAMP '2026-09-10' THEN i.amount_paid_minor ELSE 0 END)/100.0 AS paid_in_window,
 SUM(CASE WHEN i.status='open' THEN i.remaining_minor ELSE 0 END)/100.0 AS outstanding,
 SUM(CASE WHEN i.status='open' AND i.due_at<TIMESTAMP '2026-09-10'
   THEN i.remaining_minor ELSE 0 END)/100.0 AS overdue,
 SUM(CASE WHEN i.status='open' AND i.due_at IS NULL THEN i.remaining_minor ELSE 0 END)/100.0 AS undated
 FROM invoices i JOIN customer_map m USING (customer_id)
 WHERE i.currency='USD' GROUP BY m.account_id
)
SELECT a.account_name,p.open_pipeline,COALESCE(b.paid_in_window,0) AS paid_in_window,
 COALESCE(b.outstanding,0) AS outstanding,COALESCE(b.overdue,0) AS overdue,COALESCE(b.undated,0) AS undated
FROM pipeline p JOIN accounts a USING (account_id) LEFT JOIN billing b USING (account_id)
ORDER BY a.account_name;
