UPDATE orders
SET amount = amount + 5
WHERE status = '待支付' AND amount < 80;

SELECT id, amount
FROM orders WHERE status = '待支付'
ORDER BY id;
