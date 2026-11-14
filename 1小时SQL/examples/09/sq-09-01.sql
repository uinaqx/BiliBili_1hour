BEGIN;
UPDATE orders SET amount = 50 WHERE id = 101;
ROLLBACK;

SELECT id, amount FROM orders WHERE id = 101;
