SELECT id, amount, status
FROM orders
WHERE amount >= 120
  AND status = '已支付'
ORDER BY id;
