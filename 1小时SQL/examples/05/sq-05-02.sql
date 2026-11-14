SELECT c.name, o.id, o.amount
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.id
WHERE c.id = 1
ORDER BY o.id;
