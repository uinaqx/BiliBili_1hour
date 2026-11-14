SELECT customer_id, COUNT(*) AS n
FROM orders
WHERE status = '已支付'
GROUP BY customer_id
HAVING COUNT(*) >= 2
ORDER BY customer_id;
