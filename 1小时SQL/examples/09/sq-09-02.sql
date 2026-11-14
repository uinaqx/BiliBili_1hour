BEGIN;
UPDATE orders SET status = '已支付' WHERE id = 103;
UPDATE orders SET status = '已支付' WHERE id = 108;
COMMIT;

SELECT COUNT(*) AS paid
FROM orders WHERE status = '已支付';
