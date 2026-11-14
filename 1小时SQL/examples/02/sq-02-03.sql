SELECT id, status, amount
FROM orders
WHERE (status = '待支付' OR status = '已取消')
  AND amount < 100
ORDER BY id;
