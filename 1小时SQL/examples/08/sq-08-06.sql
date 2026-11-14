CREATE TABLE paid_ids (order_id INTEGER PRIMARY KEY);
INSERT INTO paid_ids (order_id)
SELECT id FROM orders WHERE status = '已支付';

SELECT COUNT(*) AS copied FROM paid_ids;
