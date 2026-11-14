SELECT id, amount
FROM orders
WHERE status IN ('已支付', '待支付')
  AND amount BETWEEN 80 AND 120
ORDER BY id;
