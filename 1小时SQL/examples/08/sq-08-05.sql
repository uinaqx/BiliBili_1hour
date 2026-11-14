SELECT id, status FROM orders WHERE id = 105;

DELETE FROM orders WHERE id = 105;

SELECT COUNT(*) AS remaining
FROM orders WHERE id = 105;
