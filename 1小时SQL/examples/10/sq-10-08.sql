CREATE VIEW paid_orders AS
SELECT id, customer_id, amount
FROM orders
WHERE status = '已支付';

SELECT COUNT(*) AS n, SUM(amount) AS total
FROM paid_orders;
