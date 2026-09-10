-- Synthetic HubSpot + QuickBooks teaching example; read-only DuckDB SQL.
-- Closed-won companies in [2026-06-12, 2026-09-10); balances at Sep 10.
-- QuickBooks-style decimal balances are already major currency units: do NOT divide by 100.
-- Expected Atlas: 20000 won value, 2 unpaid, 1250 outstanding, 1000 overdue;
-- Birch: 6000 won value, 0 unpaid, 0 outstanding, 0 overdue.
WITH
companies(company_id,company_name) AS (VALUES ('h1','Atlas'),('h2','Birch')),
customer_map(company_id,qb_customer_id) AS (VALUES ('h1','q1'),('h1','q1job'),('h2','q2')),
deals(deal_id,company_id,is_won,currency,amount,closed_at) AS (VALUES
 ('d1','h1',true,'USD',12000.00,TIMESTAMP '2026-07-10'),
 ('d2','h1',true,'USD',8000.00,TIMESTAMP '2026-08-10'),
 ('d3','h2',true,'USD',6000.00,TIMESTAMP '2026-08-15'),
 ('d4','h1',false,'USD',50000.00,TIMESTAMP '2026-09-01')),
invoices(invoice_id,qb_customer_id,currency,total_amount,balance,due_date) AS (VALUES
 ('i1','q1','USD',2000.00,1000.00,DATE '2026-09-01'),
 ('i2','q1job','USD',250.00,250.00,DATE '2026-09-20'),
 ('i3','q1','USD',1000.00,0.00,DATE '2026-09-01'),
 ('i4','q2','USD',600.00,0.00,DATE '2026-09-01')),
won AS (
 SELECT company_id,SUM(amount) AS won_deal_value FROM deals
 WHERE is_won AND currency='USD' AND closed_at>=TIMESTAMP '2026-06-12'
   AND closed_at<TIMESTAMP '2026-09-10' GROUP BY company_id
), balances AS (
 SELECT m.company_id,COUNT(*) AS unpaid_invoices,SUM(i.balance) AS outstanding,
 SUM(CASE WHEN i.due_date<DATE '2026-09-10' THEN i.balance ELSE 0 END) AS overdue
 FROM invoices i JOIN customer_map m USING (qb_customer_id)
 WHERE i.balance>0 AND i.currency='USD' GROUP BY m.company_id
)
SELECT c.company_name,w.won_deal_value,COALESCE(b.unpaid_invoices,0) AS unpaid_invoices,
 COALESCE(b.outstanding,0) AS outstanding,COALESCE(b.overdue,0) AS overdue
FROM won w JOIN companies c USING (company_id) LEFT JOIN balances b USING (company_id)
ORDER BY c.company_name;
