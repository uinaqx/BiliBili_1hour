SELECT id, status FROM orders WHERE id = 103;

UPDATE orders
SET status = '已支付'
WHERE id = 103;

SELECT id, status FROM orders WHERE id = 103;
