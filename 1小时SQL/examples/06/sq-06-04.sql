WITH paid AS (
  SELECT customer_id, SUM(amount) AS total
  FROM orders
  WHERE status = '已支付'
  GROUP BY customer_id
)
SELECT customer_id, total
FROM paid
ORDER BY total DESC, customer_id;
