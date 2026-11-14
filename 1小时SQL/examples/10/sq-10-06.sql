WITH ranked AS (
  SELECT customer_id, id, amount,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY amount DESC, id
         ) AS pos
  FROM orders WHERE status = '已支付'
)
SELECT customer_id, id, amount
FROM ranked
WHERE pos = 1
ORDER BY customer_id;
