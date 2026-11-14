SELECT c.name, COUNT(o.id) AS paid_count
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.id AND o.status = '已支付'
GROUP BY c.id, c.name
ORDER BY c.id;
