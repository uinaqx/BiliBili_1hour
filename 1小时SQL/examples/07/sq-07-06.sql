CREATE TABLE product (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  remain INTEGER NOT NULL DEFAULT 0
);
SELECT name, type, dflt_value
FROM pragma_table_info('product')
ORDER BY cid;
