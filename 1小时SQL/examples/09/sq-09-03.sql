CREATE INDEX idx_customer ON orders(customer_id);

SELECT id, amount
FROM orders
WHERE customer_id = 1
ORDER BY id;
