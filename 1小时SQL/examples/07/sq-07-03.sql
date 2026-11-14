CREATE TABLE accounts (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE
);
INSERT INTO accounts VALUES (1, 'a@example.com');
INSERT INTO accounts VALUES (2, 'a@example.com');
