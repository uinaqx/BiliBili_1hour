SELECT c.id, c.name
FROM customers AS c
WHERE EXISTS (
  SELECT 1 FROM orders AS o
  WHERE o.customer_id = c.id
    AND o.status = '待支付'
)
ORDER BY c.id;
