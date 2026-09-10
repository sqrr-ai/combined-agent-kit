-- Synthetic HubSpot + Intercom teaching example; read-only DuckDB SQL.
-- Open conversations with customer-authored messages in [Aug 27, Sep 10), 2026 UTC.
-- Parts are deduplicated to conversation grain before joining current open deals.
-- Expected: Atlas / 2 open deals / 20000.00 pipeline / 1 recent open conversation;
--           Birch / 1 open deal / 6000.00 pipeline / 0 recent open conversations.
WITH
companies(company_id,company_name) AS (VALUES ('h1','Atlas'),('h2','Birch')),
conversation_map(conversation_id,company_id) AS (VALUES ('c1','h1'),('c2','h1'),('c3','h2')),
deals(deal_id,company_id,currency,is_closed,amount) AS (VALUES
 ('d1','h1','USD',false,12000.00),('d2','h1','USD',false,8000.00),
 ('d3','h2','USD',false,6000.00),('d4','h1','USD',true,50000.00)),
conversations(conversation_id,state) AS (VALUES ('c1','open'),('c2','closed'),('c3','open')),
conversation_parts(part_id,conversation_id,author_kind,created_at) AS (VALUES
 ('p1','c1','customer',TIMESTAMP '2026-09-01'),('p2','c1','customer',TIMESTAMP '2026-09-02'),
 ('p3','c1','admin',TIMESTAMP '2026-09-03'),('p4','c2','customer',TIMESTAMP '2026-09-04'),
 ('p5','c3','customer',TIMESTAMP '2026-08-01'),('p6','c3','admin',TIMESTAMP '2026-09-05')),
open_pipeline AS (
 SELECT company_id,COUNT(*) AS open_deals,SUM(amount) AS pipeline_amount
 FROM deals WHERE NOT is_closed AND currency='USD' GROUP BY company_id
), recent_customer_conversations AS (
 SELECT DISTINCT conversation_id FROM conversation_parts
 WHERE author_kind='customer' AND created_at>=TIMESTAMP '2026-08-27'
   AND created_at<TIMESTAMP '2026-09-10'
), support AS (
 SELECT m.company_id,COUNT(DISTINCT c.conversation_id) AS recent_open_conversations
 FROM conversations c JOIN recent_customer_conversations r USING (conversation_id)
 JOIN conversation_map m USING (conversation_id)
 WHERE c.state='open' GROUP BY m.company_id
)
SELECT c.company_name,p.open_deals,p.pipeline_amount,
 COALESCE(s.recent_open_conversations,0) AS recent_open_conversations
FROM open_pipeline p JOIN companies c USING (company_id) LEFT JOIN support s USING (company_id)
ORDER BY c.company_name;
