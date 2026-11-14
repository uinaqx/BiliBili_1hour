PRAGMA foreign_keys = ON;
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    amount INTEGER NOT NULL CHECK (amount >= 0),
    status TEXT NOT NULL DEFAULT '待支付',
    ordered_on TEXT NOT NULL,
    coupon TEXT
);
INSERT INTO customers VALUES
    (1, '小林', '杭州'), (2, '小周', '上海'),
    (3, '小陈', '杭州'), (4, '小吴', '南京');
INSERT INTO orders VALUES
    (101, 1, 120, '已支付', '2026-06-01', 'NEW10'),
    (102, 2, 80, '已支付', '2026-06-02', NULL),
    (103, 1, 60, '待支付', '2026-06-03', NULL),
    (104, 3, 200, '已支付', '2026-07-01', 'VIP20'),
    (105, 2, 120, '已取消', '2026-07-02', NULL),
    (106, 3, 160, '已支付', '2026-07-03', NULL),
    (107, 1, 90, '已支付', '2026-07-04', NULL),
    (108, 2, 90, '待支付', '2026-07-05', NULL);
