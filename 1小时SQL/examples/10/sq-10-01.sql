SELECT id, amount,
       ROW_NUMBER() OVER (
         ORDER BY amount DESC, id
       ) AS pos
FROM orders WHERE status = '已支付'
ORDER BY pos;
