SELECT o.id, c.name, o.amount
FROM orders AS o
JOIN customers AS c ON c.id = o.customer_id
ORDER BY o.id
LIMIT 4;
