SELECT ROUND(AVG(amount), 2) AS average,
       MIN(amount) AS smallest,
       MAX(amount) AS largest
FROM orders
WHERE status = '已支付';
