SELECT c.name, COUNT(o.id) AS n,
       COALESCE(SUM(o.amount), 0) AS june_total
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.id AND o.status = '已支付'
 AND o.ordered_on >= '2026-06-01'
 AND o.ordered_on <  '2026-07-01'
GROUP BY c.id, c.name
ORDER BY june_total DESC, c.id;
