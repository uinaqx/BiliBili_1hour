UPDATE orders
SET amount = amount + 10
WHERE id = 102;
SELECT id, amount FROM orders WHERE id = 102;
