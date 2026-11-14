SELECT id, amount,
       CASE WHEN amount >= 120 THEN '大额'
            ELSE '普通' END AS tag
FROM orders
ORDER BY id
LIMIT 4;
