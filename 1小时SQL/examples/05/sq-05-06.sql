SELECT COUNT(*) AS joined_rows,
       COUNT(o.id) AS old_orders
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE c.id = 4;
