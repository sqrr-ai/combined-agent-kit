-- Synthetic Salesforce + Freshdesk teaching example; read-only DuckDB SQL.
-- Renewal close dates [Sep 10, Oct 10), 2026; snapshot Sep 10 00:00 UTC.
-- Aging means created >=7 full days earlier; not an SLA calculation.
-- Freshdesk defaults: status2=open,3=pending,4=resolved,5=closed; priority3=high,4=urgent.
-- Expected Atlas/15000/1 aged urgent-or-high; Birch/7000/0; Dune/4000/NULL mapping_missing.
WITH
accounts(account_id,account_name) AS (VALUES ('a1','Atlas'),('a2','Birch'),('a3','Cedar'),('a4','Dune')),
company_map(account_id,freshdesk_company_id) AS (VALUES ('a1','f1'),('a2','f2'),('a3','f3')),
opportunities(opportunity_id,account_id,deal_type,is_closed,amount,currency,close_at) AS (VALUES
 ('o1','a1','renewal',false,10000.00,'USD',TIMESTAMP '2026-09-20'),
 ('o2','a1','renewal',false,5000.00,'USD',TIMESTAMP '2026-09-25'),
 ('o3','a2','renewal',false,7000.00,'USD',TIMESTAMP '2026-09-25'),
 ('o4','a3','renewal',false,9000.00,'USD',TIMESTAMP '2026-10-10'),
 ('o5','a4','renewal',false,4000.00,'USD',TIMESTAMP '2026-09-28')),
tickets(ticket_id,freshdesk_company_id,status,priority,created_at) AS (VALUES
 ('t1','f1',2,4,TIMESTAMP '2026-09-01'),('t2','f1',3,3,TIMESTAMP '2026-09-05'),
 ('t3','f1',4,4,TIMESTAMP '2026-09-01'),('t4','f2',2,2,TIMESTAMP '2026-08-01'),
 ('t5','f2',2,3,TIMESTAMP '2026-09-03 00:00:01')),
renewals AS (
 SELECT account_id,SUM(amount) AS renewal_pipeline FROM opportunities
 WHERE deal_type='renewal' AND NOT is_closed AND currency='USD'
   AND close_at>=TIMESTAMP '2026-09-10' AND close_at<TIMESTAMP '2026-10-10'
 GROUP BY account_id
), aged AS (
 SELECT freshdesk_company_id,COUNT(DISTINCT ticket_id) AS aged_high_priority
 FROM tickets WHERE status IN (2,3) AND priority IN (3,4)
   AND created_at<=TIMESTAMP '2026-09-10'-INTERVAL '7 days'
 GROUP BY freshdesk_company_id
)
SELECT a.account_name,r.renewal_pipeline,
 CASE WHEN m.freshdesk_company_id IS NULL THEN NULL ELSE COALESCE(t.aged_high_priority,0) END AS aged_high_priority,
 CASE WHEN m.freshdesk_company_id IS NULL THEN 'mapping_missing' ELSE 'mapped' END AS coverage
FROM renewals r JOIN accounts a USING (account_id) LEFT JOIN company_map m USING (account_id)
LEFT JOIN aged t USING (freshdesk_company_id)
ORDER BY a.account_name;
