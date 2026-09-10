-- Synthetic PostHog + Stripe teaching example; read-only DuckDB SQL.
-- Cohort: accounts activated in July 2026; paid service at Aug 1 and Sep 1.
-- A paid interval is [service_start, service_end), with positive payment attributed
-- to recurring service. The normalized amount excludes unrelated one-off fees.
-- Normalized aliases are not actual Combined relations or Stripe field paths.
-- Expected: 3 activated accounts; 2 paid at baseline; 1 retained; 50.0% paid retention.
WITH
identity_map(product_user_id, account_id, stripe_customer_id) AS (VALUES
  ('u1','a1','cus1'),('u2','a1','cus1'),('u3','a2','cus2'),('u4','a3','cus3'),('u5','a4','cus4')),
product_events(event_id, product_user_id, event_name, occurred_at) AS (VALUES
  ('e1','u1','first_report_shared',TIMESTAMP '2026-07-10'),
  ('e1','u1','first_report_shared',TIMESTAMP '2026-07-10'),
  ('e2','u2','first_report_shared',TIMESTAMP '2026-07-11'),
  ('e3','u3','first_report_shared',TIMESTAMP '2026-07-20'),
  ('e4','u4','first_report_shared',TIMESTAMP '2026-07-25'),
  ('e5','u5','first_report_shared',TIMESTAMP '2026-08-01')),
paid_service(invoice_line_id, customer_id, invoice_status, amount_paid_minor, service_start, service_end) AS (VALUES
  ('l1','cus1','paid',10000,TIMESTAMP '2026-07-15',TIMESTAMP '2026-08-15'),
  ('l2','cus1','paid',10000,TIMESTAMP '2026-08-15',TIMESTAMP '2026-09-15'),
  ('l3','cus2','paid',10000,TIMESTAMP '2026-07-01',TIMESTAMP '2026-09-01'),
  ('l4','cus3','paid',0,TIMESTAMP '2026-07-01',TIMESTAMP '2026-10-01'),
  ('l5','cus3','open',10000,TIMESTAMP '2026-07-01',TIMESTAMP '2026-10-01')),
activated AS (
  SELECT DISTINCT m.account_id
  FROM product_events e JOIN identity_map m USING (product_user_id)
  WHERE e.event_name='first_report_shared'
    AND e.occurred_at >= TIMESTAMP '2026-07-01'
    AND e.occurred_at < TIMESTAMP '2026-08-01'
), account_customers AS (
  SELECT DISTINCT account_id,stripe_customer_id FROM identity_map
), coverage AS (
  SELECT a.account_id,
    MAX(CASE WHEN p.invoice_status='paid' AND p.amount_paid_minor>0
      AND p.service_start<=TIMESTAMP '2026-08-01' AND p.service_end>TIMESTAMP '2026-08-01'
      THEN 1 ELSE 0 END) AS paid_baseline,
    MAX(CASE WHEN p.invoice_status='paid' AND p.amount_paid_minor>0
      AND p.service_start<=TIMESTAMP '2026-09-01' AND p.service_end>TIMESTAMP '2026-09-01'
      THEN 1 ELSE 0 END) AS paid_followup
  FROM activated a LEFT JOIN account_customers m USING (account_id)
  LEFT JOIN paid_service p ON p.customer_id=m.stripe_customer_id
  GROUP BY a.account_id
)
SELECT COUNT(*) AS activated_accounts,SUM(paid_baseline) AS paid_at_baseline,
       SUM(CASE WHEN paid_baseline=1 AND paid_followup=1 THEN 1 ELSE 0 END) AS retained_paid_accounts,
       ROUND(100.0*SUM(CASE WHEN paid_baseline=1 AND paid_followup=1 THEN 1 ELSE 0 END)
         /NULLIF(SUM(paid_baseline),0),1) AS paid_retention_percent
FROM coverage;
