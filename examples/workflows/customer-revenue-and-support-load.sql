-- Synthetic Salesforce + Zendesk teaching example; read-only DuckDB SQL.
-- Closed-won value is a bookings proxy, not recognized revenue or cash collected.
-- USD only. Bookings window [2026-06-12, 2026-09-10); support snapshot Sep 10.
-- Expected: Atlas / 20000.00 booked / 2 unresolved / 1 high-or-urgent;
--           Birch / 15000.00 booked / 0 unresolved / 0 high-or-urgent.
WITH
accounts(account_id,account_name) AS (VALUES ('a1','Atlas'),('a2','Birch'),('a3','Cedar')),
organization_map(account_id,organization_id) AS (VALUES ('a1','z1'),('a2','z2'),('a3','z3')),
opportunities(opportunity_id,account_id,currency,is_won,amount,closed_at) AS (VALUES
  ('o1','a1','USD',true,12000.00,TIMESTAMP '2026-07-01'),
  ('o2','a1','USD',true,8000.00,TIMESTAMP '2026-08-01'),
  ('o3','a2','USD',true,15000.00,TIMESTAMP '2026-08-10'),
  ('o4','a3','USD',true,4000.00,TIMESTAMP '2026-07-10'),
  ('o5','a1','USD',false,90000.00,TIMESTAMP '2026-08-10'),
  ('o6','a1','USD',true,50000.00,TIMESTAMP '2026-06-11')),
tickets(ticket_id,organization_id,status,priority,created_at) AS (VALUES
  ('t1','z1','open','high',TIMESTAMP '2026-08-01'),
  ('t2','z1','pending','normal',TIMESTAMP '2026-05-01'),
  ('t3','z1','solved','urgent',TIMESTAMP '2026-09-01'),
  ('t4','z2','closed','normal',TIMESTAMP '2026-08-01'),
  ('t5','z3','open','urgent',TIMESTAMP '2026-09-01')),
bookings AS (
  SELECT account_id,SUM(amount) AS booked_value
  FROM opportunities WHERE is_won AND currency='USD'
    AND closed_at>=TIMESTAMP '2026-06-12' AND closed_at<TIMESTAMP '2026-09-10'
  GROUP BY account_id HAVING SUM(amount)>=10000
), backlog AS (
  SELECT m.account_id,COUNT(DISTINCT t.ticket_id) AS unresolved_tickets,
    COUNT(DISTINCT CASE WHEN t.priority IN ('high','urgent') THEN t.ticket_id END) AS high_or_urgent
  FROM tickets t JOIN organization_map m USING (organization_id)
  WHERE t.status IN ('new','open','pending','hold') AND t.created_at<TIMESTAMP '2026-09-10'
  GROUP BY m.account_id
)
SELECT a.account_name,b.booked_value,COALESCE(t.unresolved_tickets,0) AS unresolved_tickets,
       COALESCE(t.high_or_urgent,0) AS high_or_urgent
FROM bookings b JOIN accounts a USING (account_id) LEFT JOIN backlog t USING (account_id)
ORDER BY b.booked_value DESC,a.account_name;
