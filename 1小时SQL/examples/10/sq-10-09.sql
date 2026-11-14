SELECT customer_id, SUM(amount) AS total
FROM orders
WHERE status = '已支付'
GROUP BY customer_id
ORDER BY total DESC, customer_id
LIMIT 1;
