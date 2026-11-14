CREATE INDEX idx_status_date
ON orders(status, ordered_on);

SELECT id, ordered_on
FROM orders
WHERE status = '已支付'
  AND ordered_on >= '2026-07-01'
ORDER BY ordered_on, id;
