CREATE INDEX idx_customer ON orders(customer_id);

EXPLAIN QUERY PLAN
SELECT id FROM orders WHERE customer_id = 1;
