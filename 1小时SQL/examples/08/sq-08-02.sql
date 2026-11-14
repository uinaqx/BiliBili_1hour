INSERT INTO orders (id, customer_id, amount, ordered_on)
VALUES
  (110, 2, 75, '2026-07-06'),
  (111, 3, 40, '2026-07-06');
SELECT id, amount, status
FROM orders WHERE id IN (110, 111)
ORDER BY id;
