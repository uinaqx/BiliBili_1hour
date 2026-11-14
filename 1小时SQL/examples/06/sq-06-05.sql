SELECT id, '六月' AS bucket
FROM orders
WHERE ordered_on < '2026-07-01'
UNION ALL
SELECT id, '七月' AS bucket
FROM orders
WHERE ordered_on >= '2026-07-01' AND id <= 105
ORDER BY id;
