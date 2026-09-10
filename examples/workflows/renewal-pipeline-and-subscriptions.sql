-- Synthetic HubSpot + Chargebee teaching example; read-only DuckDB SQL.
-- Upcoming term ends [2026-09-10, 2026-10-10); direct subscription/deal map.
-- Expected s1/Atlas/ready; s2/Atlas/needs_renewal_deal; s3/Birch/cancellation_review.
-- A general account deal does not automatically cover every subscription.
WITH
companies(company_id,company_name) AS (VALUES ('h1','Atlas'),('h2','Birch')),
customer_map(company_id,customer_id) AS (VALUES ('h1','cb1'),('h2','cb2')),
subscriptions(subscription_id,customer_id,status,term_end) AS (VALUES
 ('s1','cb1','active',TIMESTAMP '2026-09-15'),('s2','cb1','active',TIMESTAMP '2026-09-25'),
 ('s3','cb2','non_renewing',TIMESTAMP '2026-09-20'),('s4','cb2','active',TIMESTAMP '2026-10-10')),
deals(deal_id,company_id,deal_type,is_closed,expected_close) AS (VALUES
 ('d1','h1','renewal',false,TIMESTAMP '2026-09-12'),
 ('d2','h1','expansion',false,TIMESTAMP '2026-09-15'),
 ('d3','h2','renewal',true,TIMESTAMP '2026-09-15')),
subscription_deal_map(subscription_id,deal_id) AS (VALUES ('s1','d1'),('s2','d2'),('s3','d3')),
coverage AS (
 SELECT s.subscription_id,m.company_id,s.status,s.term_end,
   COUNT(DISTINCT CASE WHEN d.deal_type='renewal' AND NOT d.is_closed
     AND d.company_id=m.company_id AND d.expected_close<=s.term_end THEN d.deal_id END) AS covering_deals
 FROM subscriptions s JOIN customer_map m USING (customer_id)
 LEFT JOIN subscription_deal_map dm USING (subscription_id)
 LEFT JOIN deals d USING (deal_id)
 WHERE s.status IN ('active','non_renewing') AND s.term_end>=TIMESTAMP '2026-09-10'
   AND s.term_end<TIMESTAMP '2026-10-10'
 GROUP BY s.subscription_id,m.company_id,s.status,s.term_end
)
SELECT c.subscription_id,h.company_name,c.term_end,c.covering_deals,
 CASE WHEN c.status='non_renewing' THEN 'cancellation_review'
      WHEN c.covering_deals=0 THEN 'needs_renewal_deal' ELSE 'ready' END AS next_action
FROM coverage c JOIN companies h USING (company_id)
ORDER BY c.subscription_id;
