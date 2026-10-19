from author import chapter,scene
c=chapter('10','模块与文件','Modules and Files',6)
scene(c,'10-1','使用已经准备好的模块','''很多常用工具已经由Python整理好了，不必每次自己重写。模块可以先理解成一组放在一起、能够被导入使用的工具。import math 以后，就能通过 math 点工具名调用相应功能。
sqrt 用来开平方，九的平方根显示三点零；ceil 向上取整，十二点三得到十三。这里 math 是Python自带的标准库模块，不需要为了这个例子另外安装软件包。
也可以用 from math import sqrt，只导入这里要使用的名字，后面直接写 sqrt。两种常见写法先认清一个重点：这个功能来自哪里，后面应该用什么名字调用。不要不加选择地导入一大堆名字，导致阅读时不知道某个工具属于谁。现在先使用标准库，再看怎样把自己写的小函数放进另一个文件。''',r'''import math

print(math.sqrt(9))
print(math.ceil(12.3))
from math import sqrt
print(sqrt(16))''','3.0\n13\n4.0\n',['import math 后用 math.工具名','from ... import ... 可导入指定名字','math 是自带模块，本例无需安装包'],diagram='module')
TOOLS='def within(spent, budget):\n    return spent <= budget\n'
MAIN='from budget_tools import within\n\nprint(within(25, 30))\n'
scene(c,'10-2','把自己的函数放进另一个文件','''自己写的函数也可以整理成模块。画面中的 within 放在 budget_tools 点 py 文件，另一个 main 点 py 从它导入 within，再交入二十五和三十，得到 True。
这两个文件在本例中放进同一个文件夹。导入时写 budget_tools，不再把点 py 后缀也写进去。配套目录提供了两个完整文件，你可以分别打开，核对定义在哪里、调用在哪里。
拆文件是为了按功能组织内容，不是把代码随意挪走就一定能找到。先让同目录这个最简单情况运行起来。还要避免把自己的文件取名为 math 点 py 这类已经常用的模块名，否则可能把原本想使用的工具遮住。初学阶段保持文件名清楚、目录简单，比急着建立很深的工程结构更有帮助。''',TOOLS,'True\n',['budget_tools.py 保存函数定义','main.py 导入并调用这个函数','本例两个文件放在同一目录'],diagram='own-module',filename='budget_tools.py',full=MAIN,fixtures={'budget_tools.py':TOOLS})
scene(c,'10-3','把一小段数据写进文件','''前面数据都在程序运行时使用，程序结束以后，如果希望记录还能留在硬盘里，就可以写入文件。open 接收文件名和打开方式，w 表示写入；encoding 指定文字采用UTF八编码，便于一致地保存和读取。
with 后面的缩进范围负责这次文件使用，as file 给打开的文件起个临时名字。file 点 write 把文字写进去，文字中的反斜杠和字母 n 组合，在这里表示换行，所以文件内容是十二和八两行。注意反斜杠的方向和普通除法斜杠不同。
w 模式会覆盖原有内容，不能拿不希望覆盖的重要文件随便试。请在配套练习的独立目录运行。本页不需要展开底层细节，先记住打开方式、写入内容，以及离开 with 范围后文件会正常关闭这几个步骤。''',r'''with open("expenses.txt", "w", encoding="utf-8") as file:
    file.write("12\n8\n")
print("saved")''','saved\n',['w 写入模式会覆盖原有内容',r'文字里的 \n 表示换行','离开 with 范围，文件会关闭'],diagram='file-write',files={'expenses.txt':'12\n8\n'})
scene(c,'10-4','逐行读取已经保存的数据','''读取已有文件时，把打开方式改为 r。这里费用文件已经有十二和八两行，for 可以依次取得每行文字。line 先去掉两端空白，再转换成整数，加进 total，最终显示二十。
文件里的数字仍然先按文字读出来，不会因为我们知道它表示开销，就自动成为整数。这和 input 读到内容后需要转换的道理相同。
相对文件名会从程序当前使用的工作目录寻找，本课示例要在各自文件夹里运行，资料里已经放好需要的费用文件。如果文件不存在，或者某一行不是合法整数，也可能失败，下一章会继续介绍处理方式。先用合法数据走一遍完整路线：打开、逐行读、整理、转换、累加、关闭。''',r'''total = 0
with open("expenses.txt", "r", encoding="utf-8") as file:
    for line in file:
        amount = int(line.strip())
        total += amount
print(total)''','20\n',['配套文件已有两行：12 和 8','每行先是文字，需要转换成整数','逐行累加，最终得到 20'],diagram='file-read',fixtures={'expenses.txt':'12\n8\n'})
scene(c,'10-q','课堂练习：写入是覆盖还是追加','''本题开始时，expenses 点 txt 已经保存了十二和换行。现在用 w 模式打开，写入八和换行，再读出文件内容。最后会同时看到十二和八，还是只看到八？
请特别看打开模式，不要只因为我们又调用了一次 write，就把它理解成一定接在旧内容后面。
给你四秒，先预测最终文件里有什么，再说明如果想保留原来那笔十二，需要换成什么模式。练习目录提供了本题的初始文件，请只在这份独立例子里操作，方便准确观察变化。''',r'''with open("expenses.txt", "w", encoding="utf-8") as file:
    file.write("8\n")
with open("expenses.txt", "r", encoding="utf-8") as file:
    print(file.read().strip())''','8\n',['原文件内容：12，然后换行','重点看打开方式是 w','预测写完以后真正保存的内容'],kind='question',fixtures={'expenses.txt':'12\n'},files={'expenses.txt':'8\n'})
scene(c,'10-a','答案：w 覆盖，a 才接在末尾','''原题只显示八，因为 w 打开时会清除旧内容，再写入新文字。它并没有替我们保留原来的十二。
如果需要接在末尾，就使用 a，表示追加。修正版在初始文件十二之后写入八，最后读到两行，分别是十二和八。注意，初始文件本来就有换行，所以追加的八能从下一行开始；追加操作本身不会替每一笔数据自动补好分隔。
文件练习不仅要检查屏幕显示，还要看实际保存的内容和打开方式。现在我们已经把开销从键盘、变量、列表，一直连接到硬盘文件。下一步处理输入或读取不符合预期时的情况，让程序能给出清楚的回应。''',r'''with open("expenses.txt", "a", encoding="utf-8") as file:
    file.write("8\n")
with open("expenses.txt", "r", encoding="utf-8") as file:
    print(file.read().strip())''','12\n8\n',['原题 w 覆盖，所以只剩 8','修正版 a 追加，保留原来的 12','换行等分隔要由写入内容明确提供'],diagram='file-append',fixtures={'expenses.txt':'12\n'},files={'expenses.txt':'12\n8\n'})
c=chapter('11','异常处理','Exceptions',4)
scene(c,'11-1','输入不合适时给出清楚提示','''回到键盘输入。如果使用者交入 abc，int 无法把它转换成整数，会报告 ValueError。把可能失败的操作放在 try 的缩进范围，用 except 指定处理这种异常，就能显示自己的提示。
转换失败以后，try 里剩下的显示不会继续执行，而是跳到对应的 except，显示 not an integer。处理结束后，再继续执行结构外面的 done。如果输入十二，转换成功，显示十二，不进入这段异常处理。
不要因为学会 except，就把所有代码都塞进去，或者捕获以后什么也不解释。先知道哪一步可能失败，具体是什么问题，应该怎样回应。本页只处理数字转换失败，其他不相关的问题仍应让我们看见，便于找到真正原因。''',r'''text = input()
try:
    amount = int(text)
    print(amount)
except ValueError:
    print("not an integer")
print("done")''','not an integer\ndone\n',['本页输入：abc，转换失败','try 尝试操作，except 处理指定异常','处理后继续执行外面的 done'],diagram='exception',stdin='abc\n',runs=[dict(stdin='abc\n',expected='not an integer\ndone\n'),dict(stdin='12\n',expected='12\ndone\n')])
scene(c,'11-2','按约定拒绝不合适的数据','''有时输入虽然能转换成整数，却不符合程序自己的规则。例如当前这个记录普通支出的函数，规定金额不能为负。require_amount 检查到负数，就用 raise 主动报告 ValueError，并说明 negative amount。
完整程序在调用处交入负五，再用 except 取得错误对象，把里面的提示显示出来。换成正数，就会正常返回金额。报告异常之后，不会再继续走这次函数里后面的正常返回。
不是每个判断都必须用异常。比较有没有超预算，用 if 就能表达；当一个函数不能按约定完成任务时，再清楚报告失败，让调用处决定怎样处理。先把正常返回和失败处理这两条路线分清，比盲目记住很多错误名称更重要。''',r'''def require_amount(amount):
    if amount < 0:
        raise ValueError("negative amount")
    return amount''','negative amount\n',['本例规定普通支出金额不能为负','raise 主动报告不能按约定完成','调用处 except 后显示错误提示'],diagram='validation',after='try:\n    print(require_amount(-5))\nexcept ValueError as error:\n    print(error)')
scene(c,'11-q','课堂练习：失败后会经过哪些行','''沿着这段程序看字母的显示顺序。先显示 A，再把 abc 转成整数，然后还有显示 B。except 里面显示 C，整个结构外面显示 D。
转换失败时，最终会显示哪些字母？请注意，except 不是每次必定执行的另一组普通操作，失败以后也不会自动回到 try 里补做 B。
给你四秒，在纸上画出正常向下和转去处理问题的两条路线，选择这次真正经过的那一条。用具体步骤检查执行顺序，比只背一串输出字母更有意义。''',r'''try:
    print("A")
    int("abc")
    print("B")
except ValueError:
    print("C")
print("D")''','A\nC\nD\n',['转换前的 A 已经执行','失败后转去对应 except','结构外的 D 随后执行'],kind='question')
scene(c,'11-a','答案：失败时跳过 B','''原题依次显示 A、C、D。转换前的 A 已经显示，int 失败以后跳到 except，显示 C，再执行结构外的 D。B 被跳过。
画面改用合法的十二作为对照。转换成功后继续显示 B，不进入 except，所以这次是 A、B、D。把两种数据放在同样的结构里观察，能看清异常究竟改变了哪一步。
以后遇到一长段错误提示，先读具体错误种类和自己代码对应的那一行，找到无法完成的操作。能改正写法或数据，就先修正；确实需要应对的失败，再设计合适提示或后续动作。不要用一个空处理把问题全部藏起来，程序没有报错显示，不等于已经做对了事情。''',r'''try:
    print("A")
    int("12")
    print("B")
except ValueError:
    print("C")
print("D")''','A\nB\nD\n',['原题失败路线：A → C → D','对照成功路线：A → B → D','只经过本次实际满足的路线'],diagram='exception-routes')
c=chapter('12','综合回顾','Review',2)
scene(c,'12-1','用具体问题检查每一步','''现在回顾这条主线。变量给数据起名字，表达式计算结果，input 接收文字，print 把信息显示出来。条件决定选哪条路，循环重复处理一组数据。
列表保存有位置的多项内容，字符串保存文字，字典按键找值；元组和集合又各有用途。函数把步骤整理成可调用的小工具，模块把工具组织起来，文件让数据在程序结束以后仍能留下。异常处理负责应对某些无法正常完成的操作。
这些名字不必一次全背熟。读代码时先问：现在是什么数据？下一条操作改了谁？判断走哪边？循环何时结束？如果是函数，交入了什么，返回值有没有被使用？每次跟踪一个具体变化，就能把稍长的程序拆成已经认识的小步骤。''',notes=['数据：变量、类型、列表与字典','流程：输入输出、判断与循环','组织：函数、模块与文件','遇到问题：读原因，再决定怎样处理'],diagram='recap')
scene(c,'12-2','把基础连成一份开销小助手','''最后把熟悉的步骤连起来。expenses 保存十二、八、五，budget 是三十。sum 算出总额二十五，再把总额和预算交给 within，判断是否不超过预算。
这次返回 True，所以显示余额五。如果把列表里的五改成十五，总额变成三十五，判断就会走另一边，显示 over。先预测这个变化，再动手运行，你就能验证整条处理路线。
课后可以继续让用户输入每笔开销，把记录存进文件，再增加按商品名称查询价格的功能。不要一次全改，先完成一个能解释清楚的小步骤，再加下一步。今天的目标是让你独立读懂、改写和运行这些入门程序。熟悉之后再继续学习更完整的项目组织、类与对象，以及自己感兴趣的应用方向。把第一批小程序亲手做出来，下一阶段就有了清楚的起点。''',r'''def within(spent, budget):
    return spent <= budget

expenses = [12, 8, 5]
budget = 30
total = sum(expenses)
print(f"total={total}")
if within(total, budget):
    print(f"remaining={budget - total}")
else:
    print("over")''','total=25\nremaining=5\n',['12 + 8 + 5 得到总额 25','within 判断是否不超过预算 30','预算内显示余额 5，否则显示 over'],diagram='final')
