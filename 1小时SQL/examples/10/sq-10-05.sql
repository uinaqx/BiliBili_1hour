WITH paid AS (
  SELECT customer_id, SUM(amount) AS total
  FROM orders WHERE status = '已支付'
  GROUP BY customer_id
)
SELECT COUNT(*) AS paying_customers,
       SUM(total) AS paid_revenue
FROM paid;
