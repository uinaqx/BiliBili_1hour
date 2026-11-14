SELECT id, amount,
       amount + 5 AS with_delivery
FROM orders
ORDER BY id
LIMIT 3;
