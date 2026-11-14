from author import chapter, page

c=chapter('事务与索引')
page(c,'用 ROLLBACK 撤销练习修改','''
BEGIN;
UPDATE orders SET amount = 50 WHERE id = 101;
ROLLBACK;

SELECT id, amount FROM orders WHERE id = 101;
''',['BEGIN 开启事务','UPDATE 在事务中把 101 改为 50','ROLLBACK 撤销修改，恢复到 120'],
'[1]有时需要把多条操作作为一组处理。这一组叫事务。BEGIN 显式开始一次事务。在这套练习数据库里，编号一百零一的金额原来是一百二十。[2]这里临时把它改成五十。如果同一个连接在回退前查询，就能看到自己刚做的修改。',
'[3]接下来运行 ROLLBACK，把尚未提交的修改撤销。[5]事务结束后，再查编号一百零一，金额回到一百二十。以后练习写入数据时，你可以先开启事务，执行修改和查询，验证反馈后再决定提交或回退。把执行过程分成这几个阶段，就能很清楚地知道什么时候只是试改，什么时候已经保存。')
page(c,'用 COMMIT 保存一组修改','''
BEGIN;
UPDATE orders SET status = '已支付' WHERE id = 103;
UPDATE orders SET status = '已支付' WHERE id = 108;
COMMIT;

SELECT COUNT(*) AS paid
FROM orders WHERE status = '已支付';
''',['两笔补款操作放入同一事务','COMMIT 提交两次状态修改','提交后已支付订单为七笔'],
'[1,2,3]练习数据里有两笔待支付订单，这次假设它们都补款成功。先开启事务，再按各自的编号修改状态。一开始已付款五笔，两次修改分别让一百零三和一百零八进入这个口径。此时可以在同一连接预览修改后的状态。',
'[4]确认以后用 COMMIT 提交这一组修改，数据库结束事务并保存。[6,7]再统计已支付订单，得到七笔。如果在提交前发现某个编号填错，就执行 ROLLBACK，再重新开始。真实程序通常在操作失败后先处理错误并按需要回退。这一页的两条更新都成功，因此可以一起提交。')
page(c,'用索引服务常见查找','''
CREATE INDEX idx_customer ON orders(customer_id);

SELECT id, amount
FROM orders
WHERE customer_id = 1
ORDER BY id;
''',['索引按指定字段组织查找路径','查询仍按 WHERE 描述需求','筛出的三笔订单及排序与以前相同'],
'[1]如果订单很多，经常按客户编号找记录，就可以为这个字段建索引。把它想成书末的索引页，按一个键帮你定位可能的记录位置。CREATE INDEX 后给索引一个名字，再说明哪张表的哪一列。这个索引针对 orders 的 customer id。',
'[3,4,5,6]创建完以后，查询写法照常。按一号客户筛选，再按订单编号输出一百零一、一百零三和一百零七。索引主要帮助数据库选择访问方式，结果依然由查询语句决定。维护索引需要存储空间，插入和修改时也要更新它。先找项目里经常执行的查询，再决定要为哪些列建立索引。')
page(c,'用查询计划看 SQLite 怎样找行','''
CREATE INDEX idx_customer ON orders(customer_id);

EXPLAIN QUERY PLAN
SELECT id FROM orders WHERE customer_id = 1;
''',['EXPLAIN QUERY PLAN 查看选用的访问方式','本机结果显示使用 idx_customer','具体计划随数据、索引及 SQLite 版本变化'],
'[1]为了观察索引是否被选用，先建一个客户编号索引。[3,4]接着把 EXPLAIN QUERY PLAN 放在现有查询前面。它返回数据库计划怎样访问数据。我们想知道这次会按客户编号查索引，还是扫描表中的行。通常先把这个命令用于经常执行、看起来慢的查询。',
'[3,4]这一例的计划里能找到 SEARCH 和索引 idx customer，说明执行器选择通过索引定位记录。这里显示的是访问计划，下一次直接运行 SELECT 才会得到查询结果。[1]换成真实项目，可以先记录旧计划，建索引后再看一次，并在有代表性的数据上测时间。数据分布和查询写法都会影响数据库的选择。')
page(c,'理解复合索引的列顺序','''
CREATE INDEX idx_status_date
ON orders(status, ordered_on);

SELECT id, ordered_on
FROM orders
WHERE status = '已支付'
  AND ordered_on >= '2026-07-01'
ORDER BY ordered_on, id;
''',['复合索引先组织状态，再组织日期','该查询固定状态并指定日期范围','三个七月已支付订单符合条件'],
'[1,2]索引还可以同时包含两个字段。这里先写状态，再写日期，可以想成先把订单按状态放进不同分区，再在每个分区里按日期排列。查询如果先确定已支付，再取某个日期区间，这个排列方式就很适合查找。',
'[4,5,6,7]本页先找已支付，再限制从七月开始。结果是七月一日、三日和四日三笔。[8]最后按日期和编号排序。设计复合索引时，先把查询中最常用的条件写出来，观察是按哪个字段精确定位、再按哪个字段查范围。判断是否用上索引，仍然可以套上上一页的查询计划命令。')
page(c,'练习 · 回滚发生在查询前','''
BEGIN;
DELETE FROM orders WHERE id = 105;
ROLLBACK;

SELECT id, status FROM orders WHERE id = 105;
''',['删除发生在显式事务内','ROLLBACK 执行在最终查询之前','查询仍能找到 105 号已取消订单'],
'[1,2]题目先打开事务，再删除一百零五号。删除语句本身会命中订单表中那一条已取消记录。[3,5]看清回滚和查询的先后顺序。暂停几秒，分别写下回滚前能不能查到这条记录，回滚后屏幕会显示什么。想想把第三行换成提交以后，答案会怎样变化。',
'[2]删除以后，同一连接立刻查这笔订单会查不到。[3]接着回滚，删除被撤销。[5]所以最终查询仍然返回一百零五号，状态是已取消。若把回滚改成提交，删除就会保留下来，查询返回零行。做事务题时，把开始点、每项写入和结束点划在时间线上，很容易看清最后保存了什么。',kind='exercise',expected=[[105,'已取消']])

c=chapter('窗口函数与综合报表')
page(c,'给每笔订单标上顺序号','''
SELECT id, amount,
       ROW_NUMBER() OVER (
         ORDER BY amount DESC, id
       ) AS pos
FROM orders WHERE status = '已支付'
ORDER BY pos;
''',['ROW_NUMBER 为窗口中的每行编号','金额降序、编号升序决定编号','五笔已支付订单依然各占一行'],
'[5]先留已支付的五笔。现在想显示每笔金额，还希望附带从大到小的顺序号。[2,3,4]ROW NUMBER 负责生成顺序号。OVER 的括号中写金额降序，同金额时按订单号升序。数据库依次给结果行编号，从一开始。和前面的分组汇总相比，每笔明细在这里都保留下来。',
'[1,2,4]屏幕显示订单号、金额和名次。最先是两百那笔，接着一百六十，然后一百二十、九十、八十。[6]最后的 ORDER BY 让输出按顺序号排列。窗口里的排序决定怎么计算编号，外层排序决定怎么展示结果。自己写时可以分别问，计算顺序是什么，呈现给读者的顺序又是什么。')
page(c,'用 PARTITION BY 给每位客户单独编号','''
SELECT customer_id, id, amount,
       ROW_NUMBER() OVER (
         PARTITION BY customer_id
         ORDER BY amount DESC, id
       ) AS pos
FROM orders WHERE status = '已支付'
ORDER BY customer_id, pos;
''',['PARTITION BY 按客户分区','每个客户从 1 开始编号','一号两笔，二号一笔，三号两笔'],
'[1,6]改一个需求。现在想知道每位客户各自的最大订单。先保留已支付的明细，同时展示客户号、订单号和金额。[2,3,4]给 ROW NUMBER 增加 PARTITION BY customer id。把记录按客户分成不同的分区，再在各区按金额从大到小排序。每个分区自己的编号都从一开始。',
'[7]最终按客户号和各自的编号输出。客户一号先一百二十后九十。二号只有八十。三号先二百后一百六十。位置一在每个客户分区都会出现。[3,4]如果改为按下单日期排序，位置一就表示这位客户时间最早的订单。分区回答谁和谁一起排，排序回答组里谁在前。')
page(c,'报表第一步 · 计算每位客户的付款汇总','''
SELECT c.id, c.name, COUNT(o.id) AS n,
       COALESCE(SUM(o.amount), 0) AS total
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.id AND o.status = '已支付'
GROUP BY c.id, c.name
ORDER BY total DESC, c.id;
''',['客户表放左侧，保留未下单客户','COUNT 统计付款笔数，SUM 汇总金额','四行合计 650 元，最后一行总额为 0'],
'[3,4,5]从这里做一份可实际使用的付款报告。目标是每个客户一行，显示姓名、付款笔数、付款总额，包含零笔客户。客户表放在左边。只在 ON 中匹配已支付订单。[6]每个客户一组。先数右表订单编号，再加总金额，方便一起检查这两个指标。',
'[1,2]小林两笔，二百一十。小周一笔，八十。小陈两笔，三百六十。小吴没有匹配，COUNT 返回零，SUM 的空结果由 COALESCE 显示为零。[7]最后按总金额降序，得到小陈、小林、小周、小吴。先把这一步的数字核对好，下一页再加总额排名。')
page(c,'报表第二步 · 在汇总结果上计算排名','''
WITH paid AS (
  SELECT c.id, c.name,
         COALESCE(SUM(o.amount), 0) AS total
  FROM customers AS c
  LEFT JOIN orders AS o
    ON o.customer_id = c.id AND o.status = '已支付'
  GROUP BY c.id, c.name
)
SELECT name, total,
       DENSE_RANK() OVER (ORDER BY total DESC) AS rank
FROM paid
ORDER BY rank, id;
''',['WITH 提供每位客户的一行汇总','DENSE_RANK 对并列总额给同一名次','外层使用编号稳定安排并列的显示顺序'],
'[1,2,3,4,5,6,7]把上一页的汇总装进 WITH。中间结果包含客户编号、姓名、总额，仍然每人一行。可以先执行括号里的查询，核对小吴为零。[9,10]外层显示姓名和总额，再用 DENSE RANK 按总额降序编号。两个总额相同时，它们会拿到同一名次，下一个不同金额接下一名。',
'[11,12]这四个人金额都不同，名次依次是一到四。最后按名次和客户编号显示，使并列时仍有可预测的展示顺序。[10]这里名次只看金额。把客户编号也写入窗口排序的话，同额的人会被当成不同的排序键。做这类题，先定义并列规则，再决定用普通顺序号还是允许并列的名次。')
page(c,'读懂报表的几层计算','''
WITH paid AS (
  SELECT customer_id, SUM(amount) AS total
  FROM orders WHERE status = '已支付'
  GROUP BY customer_id
)
SELECT COUNT(*) AS paying_customers,
       SUM(total) AS paid_revenue
FROM paid;
''',['内层是一人一行的付款汇总','外层将客户汇总再合成一行','三位客户合计支付 650 元'],
'[1,2,3,4]综合报表交付之前，再做一次总数校验。这里从同一份初始数据出发，先按客户统计已支付总额。这一步直接从订单表开始，因此只得到有付款的三位客户。中间三行是二百一十、八十和三百六十。[6,7,8]外面统计三行的数量与总和。',
'[6,7]结果得到三位有付款的客户，总金额六百五十元。把这个总额拿去对照直接从订单求和的结果，两边一致。做报表时很适合用这种独立口径来交叉核对。[2,4]回看整条 SQL，可以说清内层一行是一位客户，外层只剩一行表示经营总览。先搞清每一层的一行是什么，再数返回行。')
page(c,'练习 · 每位客户最贵的一笔已支付订单','''
WITH ranked AS (
  SELECT customer_id, id, amount,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY amount DESC, id
         ) AS pos
  FROM orders WHERE status = '已支付'
)
SELECT customer_id, id, amount
FROM ranked
WHERE pos = 1
ORDER BY customer_id;
''',['中间表按客户独立给订单排名','pos = 1 各取第一笔','结果为一号 101、二号 102、三号 104'],
'[1,2,3,4,5,6,7]最后一道题。先取已支付的订单，按客户分区，再按金额从高到低编号。[9,10,11,12]外层只留每区的位置一。给自己几秒钟，写下每位客户留下的订单号，再检查哪位客户没有出现在最终表里。可以从第四章用过的五笔已付款订单开始找。',
'[4,5]客户一号的位置一是一百零一，金额一百二十。二号只有一百零二，金额八十。三号的位置一是一百零四，金额两百。[11,12]最终三行。小吴在基础订单集中没有付款记录，因此没有分区。到这里，从表与行列、条件和排序，到分组、连接、写入、事务和窗口都用过一遍。课后可以改用六月作为时间条件，跑出一份新的客户报表。',kind='exercise',expected=[[1,101,120],[2,102,80],[3,104,200]])

page(c,'延伸练习 · 只统计六月的付款','''
SELECT c.name, COUNT(o.id) AS n,
       COALESCE(SUM(o.amount), 0) AS june_total
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.id AND o.status = '已支付'
 AND o.ordered_on >= '2026-06-01'
 AND o.ordered_on <  '2026-07-01'
GROUP BY c.id, c.name
ORDER BY june_total DESC, c.id;
''',['六月范围由月初和下个月月初确定','日期与状态都进入 ON 匹配条件','六月收款 200 元，四位客户均保留'],
'[3,4,5]做完按客户排名，再把报告改成只看六月。业务要求仍然是每位客户一行，因此客户表继续放在左边。先找编号相等、而且已经付款的订单。[6,7]接着把日期范围加进 ON。只匹配六月一日开始、七月一日之前的记录。这样没有六月付款的客户也能留下，符合报表的名单规则。',
'[1,2,8]按客户分组后，小林一百二十，小周八十，小陈和小吴都是零。六月的那笔六十元处于待支付状态，因此月报只计算前两笔。[9]按照总额降序，加编号作为并列规则。做完可以用一条简单查询，把只符合日期和状态的两笔订单拿出来相加，结果是两百。把项目查询和这个小验证写在不同文件里，之后修改报表还能重复核对。',expected=[['小林',1,120],['小周',1,80],['小陈',0,0],['小吴',0,0]])
page(c,'延伸练习 · 用视图保存查询规则','''
CREATE VIEW paid_orders AS
SELECT id, customer_id, amount
FROM orders
WHERE status = '已支付';

SELECT COUNT(*) AS n, SUM(amount) AS total
FROM paid_orders;
''',['视图保存一条查询的定义','查询时按当前订单表计算','本例输出五笔与 650 元'],
'[1,2,3,4]如果经营总览和付款月报都经常使用已支付订单，可以考虑给这个查询固定一个名字。用 CREATE VIEW 建立视图 paid orders。定义里的 SELECT 说明它提供哪些列和哪些行。以后读这个名字，就能拿到当前已支付的订单明细。和本章前面学到的一次性 WITH 相比，这个视图定义会作为数据库里的对象保存下来。',
'[6,7]建好视图以后，对它做计数和求和，结果是五笔、六百五十元。如果订单表里的状态以后改变，再查询这个普通视图就按新的数据计算。把经常用的筛选写成视图，可以让多个查询沿用同一口径。第一次使用视图时，先单独执行视图定义里的 SELECT，确认筛选的行和列，再给它起一个说明用途的名字。',expected=[[5,650]])
page(c,'回顾 · 把一个问题翻译成查询','''
SELECT customer_id, SUM(amount) AS total
FROM orders
WHERE status = '已支付'
GROUP BY customer_id
ORDER BY total DESC, customer_id
LIMIT 1;
''',['先问结果一行代表什么','再确定数据来源、过滤和排序','付款总额最高的是客户三号'],
'[1,2]最后用一句常见需求回顾，找出累计付款最多的客户。先问结果的一行应该代表什么。这里一行代表一个客户，需要客户编号和总额。原始数据来自订单表，原表一行是一笔订单。[3,4]先只留已支付的订单，再按客户编号分组。这样每组的金额合计才是这个客户的累计付款。',
'[5,6]汇总后从大到小排，金额一样就按客户编号，取第一行。最后查到三号，三百六十元。需要姓名时，可以再把它和客户表按编号连上。[1]课后从工程里的初始化脚本开始，把基础查询、六月报表和回滚练习各跑一遍，再换一个门槛或月份。每次先预测行数和关键结果，执行以后再核对。这套习惯会比背下所有关键词更有用。',expected=[[3,360]])
