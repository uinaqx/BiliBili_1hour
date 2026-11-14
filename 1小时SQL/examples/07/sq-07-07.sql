SELECT name, type, "notnull", pk
FROM pragma_table_info('orders')
WHERE name IN ('id', 'customer_id', 'coupon')
ORDER BY cid;
