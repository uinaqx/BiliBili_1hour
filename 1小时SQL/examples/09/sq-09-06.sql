BEGIN;
DELETE FROM orders WHERE id = 105;
ROLLBACK;

SELECT id, status FROM orders WHERE id = 105;
