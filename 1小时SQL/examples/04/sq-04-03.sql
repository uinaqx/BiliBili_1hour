SELECT status, COUNT(*) AS n,
       SUM(amount) AS total
FROM orders
GROUP BY status
ORDER BY status;
