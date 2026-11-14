SELECT COUNT(*) AS n,
       SUM(amount) AS total
FROM orders
WHERE status = '已支付';
