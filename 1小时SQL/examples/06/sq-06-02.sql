SELECT id, name
FROM customers
WHERE id IN (
  SELECT customer_id FROM orders
  WHERE amount >= 150
)
ORDER BY id;
