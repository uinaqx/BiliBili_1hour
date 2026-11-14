CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  price INTEGER NOT NULL,
  weight REAL
);
INSERT INTO products VALUES (1, '笔记本', 12, 0.18);
SELECT * FROM products;
