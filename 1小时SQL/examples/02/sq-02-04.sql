SELECT id, ordered_on
FROM orders
WHERE ordered_on >= '2026-06-01'
  AND ordered_on <  '2026-07-01'
ORDER BY ordered_on, id;
