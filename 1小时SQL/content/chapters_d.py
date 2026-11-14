from author import chapter, page

c=chapter('建表与约束')
page(c,'用 CREATE TABLE 定义数据形状','''
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  price INTEGER NOT NULL,
  weight REAL
);
INSERT INTO products VALUES (1, '笔记本', 12, 0.18);
SELECT * FROM products;
''',['CREATE TABLE 定义字段与类型','INTEGER 保存整数，TEXT 保存文字','REAL 适合本例的小数重量'],
'[1]前面一直从准备好的表里查询，现在自己建一张商品表。CREATE TABLE 后写表名 products，括号里一行声明一列。列名表示这一栏存什么，后面的类型说明它通常接收怎样的数据。[2,3,4,5]编号和价格用整数，名称用文字，重量可以有小数，所以用 REAL。本练习里的价格都是整元。',
'[7,8]插入一条商品记录，再用 SELECT 星号读出来。编号一、笔记本、十二元、重量零点一八。每个值按这一条插入语句的位置对应到一个字段。[3,4]NOT NULL 表示名称和价格要填写。像重量这种暂时未知的项目，可以先留空。设计表时按一条真实记录，把每一项可能出现的值都想一遍。')
page(c,'主键唯一定位一行','''
CREATE TABLE tickets (
  id INTEGER PRIMARY KEY,
  buyer TEXT NOT NULL
);
INSERT INTO tickets VALUES (1, '小林');
INSERT INTO tickets VALUES (1, '小周');
''',['主键用来唯一定位一行','第二次插入复用主键 1','数据库返回唯一性约束错误'],
'[1,2,3]现在为活动门票建表。每张票有一个编号和购票人。编号被声明为主键，表内的每张票都应该拥有自己的编号。购票人可以相同，一个人能买好几张票，票号用于唯一识别哪一张。[5]先给小林存编号一。',
'[6]再尝试让小周的票也用编号一。数据库会检查主键，发现重复，第二条插入报唯一性约束错误。[2]以后想查看、修改或删除某一张特定的票，可以用这个主键写条件。姓名可能重复，主键明确对应一行。这就是订单表和客户表都设置单独编号的原因。',error='UNIQUE constraint failed')
page(c,'给邮箱加上唯一约束','''
CREATE TABLE accounts (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE
);
INSERT INTO accounts VALUES (1, 'a@example.com');
INSERT INTO accounts VALUES (2, 'a@example.com');
''',['主键与其他唯一字段可以并存','两行主键不同','邮箱重复违反 UNIQUE'],
'[1,2,3]有些字段虽然不是主键，业务也希望它保持唯一。比如练习账号表用 id 作主键，同时要求每个邮箱只注册一个账号。在 email 后写 UNIQUE，就把这项规则交给数据库检查。再加上 NOT NULL，就要求每个账号都填写邮箱。',
'[5,6]第一条写入编号一，邮箱是 a 开头的地址。第二条使用编号二，主键没有冲突，但邮箱和上一条相同。屏幕上的错误指向 accounts 的 email 列。[3]用这个例子区分两种保护，主键用来标识记录，其他唯一约束可以表达额外的业务规则。做测试时故意插入一行重复值，看看数据库指出的是哪一列。',error='UNIQUE constraint failed')
page(c,'默认值和金额范围','''
CREATE TABLE items (
  id INTEGER PRIMARY KEY,
  price INTEGER NOT NULL CHECK (price >= 0),
  status TEXT NOT NULL DEFAULT '在售'
);
INSERT INTO items (id, price) VALUES (1, 12);
SELECT id, price, status FROM items;
''',['CHECK 要求价格为非负整数范围','DEFAULT 提供省略字段的默认值','本例未写 status，存入“在售”'],
'[1,2,3]给商品价格设一个基本范围，零或者更大的金额才符合业务约定。把这个条件放进 CHECK，写入时由数据库检查。再用 NOT NULL 要求提供价格。这里用整数列保存价格，生产项目还可用 SQLite 的严格表或明确校验保证类型。[4]状态如果省略，就默认在售。',
'[6]插入时明确列出编号和价格，状态这一列没有在插入列表里。数据库会使用刚才写好的默认值。[7]查询时看到一、十二、在售。若显式传空值，NOT NULL 会检查空值。想验证 CHECK 时，另开一个练习会话，把十二改成负数运行，就能看到范围约束的反馈。')
page(c,'用外键保护订单对应的客户','''
PRAGMA foreign_keys = ON;
INSERT INTO orders (id, customer_id, amount, ordered_on)
VALUES (110, 99, 40, '2026-07-06');
''',['启用当前连接的 SQLite 外键检查','订单 customer_id 引用客户 id','初始数据没有客户 99'],
'[1]订单的客户编号应该能查到一个真实客户。配套建表语句把客户编号设成外键，引用客户表里的 id。SQLite 练习里每次连接都执行第一行，开启外键检查。这样数据库在接受订单时，会核对客户是否存在。',
'[2,3]本例故意给新订单填客户九十九。客户表只有一到四号，因此订单插入失败，数据库报外键约束错误。把客户编号改成二再运行，就能通过这个检查。[1]做关联表时，先想哪张表保存被引用的一方，再在存引用的表里声明外键。通常先导入客户，之后再导入他们的订单。',error='FOREIGN KEY constraint failed')
page(c,'看懂建表后的字段信息','''
CREATE TABLE product (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  remain INTEGER NOT NULL DEFAULT 0
);
SELECT name, type, dflt_value
FROM pragma_table_info('product')
ORDER BY cid;
''',['这是 SQLite 查看字段的写法','结果显示字段名、类型和默认值','库存列默认是 0'],
'[1,2,3,4]建一个简化的库存表。三列分别是编号、商品标题和剩余数量。库存从零开始，为它设默认值。代码写好后，可以查询表自身的结构。这个工具对接手别人的数据库也很方便，先看有哪些字段，再看每项怎么填。',
'[6,7,8]SQLite 的这项查询返回字段信息。我们选出字段名、类型和默认值，并按字段在表里的位置显示。id 类型是整数，title 是文字，remain 是整数且默认值为零。前两列的默认值显示空，说明建表时没写默认表达式。读表结构时，也可以一起查看主键和可空规则。')
page(c,'从表定义理解初始订单数据','''
SELECT name, type, "notnull", pk
FROM pragma_table_info('orders')
WHERE name IN ('id', 'customer_id', 'coupon')
ORDER BY cid;
''',['id 是订单表的主键','customer_id 明确声明了 NOT NULL','coupon 留作可选信息'],
'[1,2]回头看看整门课一直用的订单表。查询列名、类型、显式的非空标志和主键位置。SQLite 的字段信息用 notnull 表示非空标志。这里给它加双引号，按字段名读取。最后一列 pk 为一的地方，标出这一表的主键字段。',
'[3,4]只挑编号、客户编号和优惠码三列。编号是 INTEGER PRIMARY KEY，字段信息中的 pk 为一。customer id 明确写了非空，所以非空标志为一。coupon 是 TEXT，允许不填。对于这个 SQLite 整数主键，即使单独的非空标志显示零，保存下来的主键仍由数据库分配或使用提供的整数。')
page(c,'练习 · 默认值会写成什么','''
CREATE TABLE stock (
  id INTEGER PRIMARY KEY,
  units INTEGER NOT NULL DEFAULT 0
);
INSERT INTO stock (id) VALUES (8);
SELECT id, units FROM stock;
''',['INSERT 只提供了编号','units 使用默认值 0','查询得到编号 8、数量 0'],
'[1,2,3]这里有自己的库存表，每条记录存商品编号和当前数量。数量是必填整数，同时默认值是零。[5]插入语句只给出编号八，数量没有出现在插入列表里。[6]请预测最后一行会看到什么。也想一想，把默认值从零改成五，再复制这段代码到一份新的数据库中，结果会怎样。',
'[3,5]字段定义给了默认值，因此省略数量时会填零。编号来自插入语句，仍是八。[6]最后得到一行，编号八、数量零。把默认值定义改成五以后，在新建的表中执行同样的插入，就会显示五。默认值适合表达常见的起步状态，把常用状态写进表定义，录入代码就可以少填一项。',kind='exercise',expected=[[8,0]])

c=chapter('数据增删改查')
page(c,'用 INSERT 新增一行','''
INSERT INTO orders
  (id, customer_id, amount, status, ordered_on)
VALUES
  (110, 2, 75, '已支付', '2026-07-06');

SELECT id, amount, status FROM orders WHERE id = 110;
''',['列清单与 VALUES 按位置对应','新订单归属于客户二号','新增后用订单号确认结果'],
'[1,2]现在模拟新客下单，用 INSERT INTO 指定订单表。第二行列明这次提供哪些字段，依次是订单号、客户编号、金额、状态和下单日期。明确列名有一个好处，读 VALUES 时可以直接对照每个值的意思。[3,4]给订单号一百一十，客户二号，金额七十五，状态已支付，日期七月六日。',
'[4]数据库检查主键和外键后，新增这笔订单。优惠码没有提供，按练习表定义会保存为空。[6]紧接着查一百一十号。输出七十五、已支付，这样能确认写入的正是刚才填的数据。做完一条修改后，紧接着写一个明确的查询，用确定的编号把那条结果找回来。')
page(c,'用一条 INSERT 写入多行','''
INSERT INTO orders (id, customer_id, amount, ordered_on)
VALUES
  (110, 2, 75, '2026-07-06'),
  (111, 3, 40, '2026-07-06');
SELECT id, amount, status
FROM orders WHERE id IN (110, 111)
ORDER BY id;
''',['同一组列可接受多组值','VALUES 的元组用逗号连接','两笔新增订单使用默认状态'],
'[1,2,3,4]批量导入小份数据时，可以写一组列名，后接多组 VALUES。每组括号对应一行，两组之间用逗号。第一笔给客户二号金额七十五，第二笔给客户三号金额四十。每组四个值，按第一行列名的位置逐个对应。两行都省略了状态。',
'[5,6,7]用一条查询挑出刚才的两个订单号并排序。两条都显示待支付，因为初始表定义了这个默认状态。看一眼日期字段，两个日期相同，这并不影响订单编号不同。写批量录入时先用两行很小的样本测试，确认列的位置和默认值，之后再把更多同格式数据加入。')
page(c,'先预览，再用 UPDATE 修改','''
SELECT id, status FROM orders WHERE id = 103;

UPDATE orders
SET status = '已支付'
WHERE id = 103;

SELECT id, status FROM orders WHERE id = 103;
''',['第 1 行预览一百零三号订单','UPDATE 的 SET 指定新状态','同一个 WHERE 精确限定修改目标'],
'[1]订单一百零三补款成功。先查一遍这笔订单，原来是待支付。做数据修改时，可以把准备使用的 WHERE 先放进 SELECT，核对会选中谁。这里订单号是主键，因此只会查到这一单。[3,4,5]确认目标以后，用 UPDATE 写表名。SET 把状态写成已支付，WHERE 保持刚才验证过的编号。',
'[7]最后再查同一个订单号，输出已支付。这里两次查询之间只执行了一条修改，比较起来很清楚。[5]如果省略 WHERE，更新就会作用于表里所有行。写练习时先填定位条件，再补上 SET 里的字段。实际操作前，先看预览选择的行是否正是你想改的记录。')
page(c,'用旧值计算新值','''
UPDATE orders
SET amount = amount + 10
WHERE id = 102;
SELECT id, amount FROM orders WHERE id = 102;
''',['等号右侧使用当前金额','只修改编号 102','八十加十变成九十'],
'[1,2]有些修改要根据原来的值计算。比如练习中给某笔订单补十元配送费。SET 左边是要写入的金额，右边先读取当前金额，再做加法。读这样的赋值时，从右向左，算结果，再保存。[3]用主键把修改限制在一百零二号，其他订单不会经过这一步。',
'[4]一百零二原本是八十元，增加十后查询得到九十。把这个脚本重复执行一次，金额会继续变成一百。所以遇到这样的累加语句，可以先核对是否已经执行过，也可以用唯一的业务记录记录这次调整。[2]如果需求是把金额改成固定的九十，就写等号右边直接给九十。')
page(c,'用 DELETE 删除已确认的一笔','''
SELECT id, status FROM orders WHERE id = 105;

DELETE FROM orders WHERE id = 105;

SELECT COUNT(*) AS remaining
FROM orders WHERE id = 105;
''',['删除前查验目标订单','DELETE 的 WHERE 指定编号 105','删除后该编号的匹配计数为 0'],
'[1]练习数据库中，一百零五号已经取消。现在练习删除它。开始用 SELECT 把编号和状态查清楚，再执行删除。这里定位靠唯一编号。如果按状态删除，就可能命中同一状态的所有记录，因此先用原条件预览，特别容易发现范围写多了。',
'[3]DELETE FROM 后指定订单表，WHERE 指定这张单。[5,6]删除后用相同条件数行，结果是零，说明这个编号已经查不到。第二次执行这条删除，匹配行仍然是零。[1]以后要修改或删除，一般都沿用查找、确认、执行、复查的顺序。下一章会加上事务，从而在提交前还能尝试回退。')
page(c,'用 INSERT SELECT 拷贝查询结果','''
CREATE TABLE paid_ids (order_id INTEGER PRIMARY KEY);
INSERT INTO paid_ids (order_id)
SELECT id FROM orders WHERE status = '已支付';

SELECT COUNT(*) AS copied FROM paid_ids;
''',['SELECT 负责挑出已支付订单号','结果写入目标表的 order_id','本例共写入五行'],
'[1]假设现在要做一份已付款编号备份。先造一张只有订单编号的练习表。前面写 INSERT 都把值逐项列举。这一页直接把查询结果作为输入，适合从一张表挑出部分记录，再放到另一张结构不同的表。[2,3]目标列是 order id，源查询提供订单的 id。',
'[3]已经付款的订单共有五笔，查询会依次得到它们的编号。每个编号写成新表的一行。[5]最后用 COUNT 检查，目标表里确实有五行。学习这类写法时，先单跑 SELECT，检查行数和列的排列。然后加回 INSERT 的目标表和列名，验证写入行数是否和预览一致。')
page(c,'把未支付状态改成可读的批注','''
UPDATE orders
SET coupon = '待跟进'
WHERE status = '待支付' AND coupon IS NULL;

SELECT id, coupon
FROM orders WHERE status = '待支付'
ORDER BY id;
''',['AND 同时限定订单状态和空值','本例修改两条待支付订单','查询按编号验证修改范围'],
'[1,2]我们临时把优惠码一栏用作练习备注，对待支付且未填码的订单写上待跟进。真实设计可以另建备注列。这里希望练习的是怎样按多个条件批量更新数据。[3]条件一是待支付，条件二是优惠码为空。这样只改当前需要跟进的那部分记录。',
'[5,6,7]状态为待支付的有一百零三和一百零八两笔，原优惠码都是空。执行后查询这两笔，都显示待跟进。[3]如果其中一笔已经填写信息，它会在空值检查这一步被排除。批量更新前可以运行同条件的 SELECT COUNT 星号，先记下预计影响多少行，再用相同规则复查结果。')
page(c,'练习 · 一条 UPDATE 选中哪一单','''
UPDATE orders
SET amount = amount + 5
WHERE status = '待支付' AND amount < 80;

SELECT id, amount
FROM orders WHERE status = '待支付'
ORDER BY id;
''',['待支付的订单有 103 和 108','金额小于 80 的只有 103','运行结果为 103 的 65 与 108 的 90'],
'[1,2,3]题目中两笔待支付订单，金额分别是六十和九十。请用两个条件逐行判断。更新目标的金额会加五，但后面的查询范围比更新宽。[5,6,7]查询会列出所有待支付订单。你要写出两行结果，并在发生改变的那一行旁边画个圈。暂停几秒后一起核对。',
'[3]一百零三号是待支付且金额六十，通过两个条件。一百零八号虽然待支付，金额九十超过门槛。[2]只有一百零三号加五，变成六十五。[5,6,7]查看时两行都会出现，依次为一百零三、六十五，以及一百零八、九十。调试时可以同时看一笔命中和一笔刚好没命中的记录，确认更新范围。',kind='exercise',expected=[[103,65],[108,90]])
