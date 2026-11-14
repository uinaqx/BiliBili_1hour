SELECT c.name, o.id AS order_id
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE c.id IN (3, 4)
ORDER BY c.id, o.id;
