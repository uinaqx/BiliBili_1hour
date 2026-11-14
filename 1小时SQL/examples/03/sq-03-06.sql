SELECT id, amount
FROM orders
WHERE amount <= 120
ORDER BY amount DESC, id DESC
LIMIT 2;
