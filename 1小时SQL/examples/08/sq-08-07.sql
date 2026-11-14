UPDATE orders
SET coupon = '待跟进'
WHERE status = '待支付' AND coupon IS NULL;

SELECT id, coupon
FROM orders WHERE status = '待支付'
ORDER BY id;
