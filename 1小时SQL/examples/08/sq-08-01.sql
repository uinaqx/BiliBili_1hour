INSERT INTO orders
  (id, customer_id, amount, status, ordered_on)
VALUES
  (110, 2, 75, '已支付', '2026-07-06');

SELECT id, amount, status FROM orders WHERE id = 110;
