CREATE TABLE items (
  id INTEGER PRIMARY KEY,
  price INTEGER NOT NULL CHECK (price >= 0),
  status TEXT NOT NULL DEFAULT '在售'
);
INSERT INTO items (id, price) VALUES (1, 12);
SELECT id, price, status FROM items;
