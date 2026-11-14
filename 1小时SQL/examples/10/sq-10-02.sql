SELECT customer_id, id, amount,
       ROW_NUMBER() OVER (
         PARTITION BY customer_id
         ORDER BY amount DESC, id
       ) AS pos
FROM orders WHERE status = '已支付'
ORDER BY customer_id, pos;
