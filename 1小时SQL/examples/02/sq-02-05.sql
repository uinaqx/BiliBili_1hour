SELECT id, COALESCE(coupon, '无') AS coupon_name
FROM orders
WHERE coupon IS NULL AND id <= 103
ORDER BY id;
