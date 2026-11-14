SELECT c.id, c.name, COUNT(o.id) AS n,
       COALESCE(SUM(o.amount), 0) AS total
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.id AND o.status = '已支付'
GROUP BY c.id, c.name
ORDER BY total DESC, c.id;
