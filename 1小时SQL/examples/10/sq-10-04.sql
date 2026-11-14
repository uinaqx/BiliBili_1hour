WITH paid AS (
  SELECT c.id, c.name,
         COALESCE(SUM(o.amount), 0) AS total
  FROM customers AS c
  LEFT JOIN orders AS o
    ON o.customer_id = c.id AND o.status = '已支付'
  GROUP BY c.id, c.name
)
SELECT name, total,
       DENSE_RANK() OVER (ORDER BY total DESC) AS rank
FROM paid
ORDER BY rank, id;
