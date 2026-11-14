SELECT id, amount
FROM orders
WHERE amount > (
  SELECT AVG(amount) FROM orders
)
ORDER BY amount DESC, id;
