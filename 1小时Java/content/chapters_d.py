from author import chapter,scene

c=chapter('10','集合','Collections',5)
scene(c,'10-1','需要继续添加数据时使用列表','''前面用数组保存三门成绩，建立以后长度就固定了。如果新同学不断加入，人数事先还不确定，可以先学习 ArrayList 这种能够继续添加元素的列表。
尖括号里的 String 表示这里准备保存文字。new 建立一份列表，add 按先后顺序放入姓名，size 读取当前有几项，get 括号零读取第一项。列表的位置仍然从零开始。它和数组用方括号读取元素的写法不同，所以不要把两种写法混在一起。
为了使用这个现成工具，完整程序开头需要导入 java 点 util 点 ArrayList，配套示例已经写好。import 可以先理解成告诉编译器，我们这里使用哪个工具。现在先把注意力放在创建、添加和读取这三个动作上，不需要一次记住工具的所有功能。''',r'''ArrayList<String> names = new ArrayList<>();
names.add("Ana");
names.add("Bo");
System.out.println(names.size());
System.out.println(names.get(0));''','2\nAna\n',['ArrayList 可以继续添加元素','String 表示列表保存文字','位置从 0 开始，用 get 读取'],diagram='list')
scene(c,'10-2','列表里的整数与修改操作','''如果列表里要保存整数，这里写 Integer。它是 Java 为整数准备的对象类型写法，ArrayList 需要这样的类型名称。普通整数可以像画面中一样直接添加，Java 会完成相应的转换。先记住这组常用搭配，后面有基础再学习它的细节。
add 添加新的一项，set 则是修改已经存在的位置。原来的列表是八十、九十，把位置零改成八十五以后，元素数量还是两个，只有第一个值变了。
比较一下动作和结果：添加会让数量增加，修改不会。读取之前同样要保证位置有效，也就是至少为零，并且小于 size。列表能够增长，并不意味着可以随意访问一个还不存在的位置。学习新工具时，先分清它提供的操作，再观察每种操作怎样改变当前的数据。''',r'''ArrayList<Integer> scores = new ArrayList<>();
scores.add(80);
scores.add(90);
scores.set(0, 85);
System.out.println(scores.get(0));
System.out.println(scores.size());''','85\n2\n',['整数列表写 ArrayList<Integer>','add 添加，set 修改已有位置','修改第一个成绩，数量仍然为 2'],diagram='list-update')
scene(c,'10-3','按照姓名查找成绩','''列表适合按照位置读取。如果需求变成“查询 Ana 的成绩”，每次都靠自己记住 Ana 在第几个位置，就容易弄错。HashMap 可以建立姓名和成绩之间的对应关系。
这里尖括号里的两个类型，前一个 String 是用来查找的姓名，后一个 Integer 是对应的分数。姓名叫作键，分数叫作值。put 把一组对应关系保存进去，get 用姓名取出对应分数，所以查询 Ana 会得到八十。
可以把这份表理解成通讯录：输入姓名，找到相关信息。它不依靠第零个、第一个这样的顺序，也不应该用它来保证显示顺序。先按真实需要选工具：保存一串有先后位置的数据，可以考虑列表；用唯一名字查对应信息，可以考虑这种映射表。''',r'''HashMap<String, Integer> scores = new HashMap<>();
scores.put("Ana", 80);
scores.put("Bo", 90);
System.out.println(scores.get("Ana"));
System.out.println(scores.size());''','80\n2\n',['姓名是键，成绩是值','put 保存对应关系，get 按键查询','HashMap 不保证显示顺序'],diagram='map')
scene(c,'10-4','重复姓名与查不到的情况','''同一个键再次放入一个值，会替换原来的对应值，不会自动变成两位同名学生。代码先把 Ana 记为八十，再记为八十五，所以表里仍然只有一项，读到的分数是八十五。
查不到的时候也要提前想清楚。containsKey 可以判断某个键是否存在。getOrDefault 则允许我们给一个备用结果，这里查询没有保存过的 Cy，返回自己指定的零。这个零不等于已经录入了 Cy 的真实成绩，只是这次查询采用的默认值。
如果零分本身也是合法成绩，就不能仅凭返回零断定有没有记录；应该配合是否存在的判断。先明确程序想表达什么，再选择合适的分支处理，避免把缺少数据和真实数据混为一谈。''',r'''HashMap<String, Integer> scores = new HashMap<>();
scores.put("Ana", 80);
scores.put("Ana", 85);
System.out.println(scores.size() + " " + scores.get("Ana"));
System.out.println(scores.containsKey("Cy"));
System.out.println(scores.getOrDefault("Cy", 0));''','1 85\nfalse\n0\n',['同一个键再次 put，会替换旧值','containsKey 判断是否存在','默认值不代表真实录入的数据'],diagram='map-default')
scene(c,'10-q','课堂练习：删除以后的位置','''一个列表先后放入 Ana 和 Bo。remove 括号零，删除位置零的那一项。随后读取位置零，再显示列表的数量，会得到什么？
请不要把删除理解成原地留下一个空洞。先画出两个有顺序的格子，划掉第一个，再观察后面的元素应该排在哪里。
给你四秒，分别预测第一行姓名和第二行数字。这里使用的是文字列表，remove 的整数参数明确表示要删除的位置。练习要检查的是删除以后的位置变化，而不是刚才那个姓名是否还保持原来的编号。''',r'''ArrayList<String> names = new ArrayList<>();
names.add("Ana");
names.add("Bo");
names.remove(0);
System.out.println(names.get(0));
System.out.println(names.size());''','Bo\n1\n',['删除原来的第 0 项','后面的元素向前补位','再看当前位置与当前数量'],kind='question')
scene(c,'10-a','答案：剩余元素向前补位','''原题第一行显示 Bo，第二行显示一。Ana 被删除以后，Bo 成为剩下的第一项，也就是位置零，数量减少为一。
画面继续加上一个 Cy，帮助我们再核对一次。新元素接在最后，位置零仍然是 Bo，位置一是 Cy，数量回到二。可以看到，列表的位置反映当前排列，不是一张永远贴在某个人身上的编号。
这也是为什么访问列表时，应当根据它现在的 size 判断边界。添加和删除都可能改变数量，删除还可能改变后续元素的位置。如果程序需要按稳定的姓名或编号查记录，就应该另外建立对应关系，不能把某次读到的位置当成永远有效的身份。''',r'''ArrayList<String> names = new ArrayList<>();
names.add("Ana");
names.add("Bo");
names.remove(0);
names.add("Cy");
System.out.println(names.get(0) + " " + names.get(1));
System.out.println(names.size());''','Bo Cy\n2\n',['原题：Bo、1；删除后向前补位','新添 Cy 后：Bo、Cy，共 2 项','当前位置与稳定身份要分清'],diagram='list-remove')

c=chapter('11','异常处理','Exceptions',4)
scene(c,'11-1','文字不一定能转换成整数','''最后学习程序遇到问题时的一种处理方法。Integer 点 parseInt 可以把表示整数的文字变成整数。比如文字八十可以转换，但 abc 并不表示一个整数，这次操作就无法正常完成。
Java 会报告一个叫 NumberFormatException 的异常。把可能失败的操作放在 try 里面，用 catch 接住这种具体问题，就可以显示自己的提示，然后继续执行后面的语句。
看这段代码：转换失败后，不会得到一个假装成功的数字，而是跳到对应的 catch，显示 not a number。处理完以后，继续显示 continue。如果把文字改为八十，转换成功，显示八十，catch 里面的提示就不会执行。先分清正常路线和失败路线，异常处理就有了具体含义，不只是多背一组括号。''',r'''String text = "abc";
try {
    int value = Integer.parseInt(text);
    System.out.println(value);
} catch (NumberFormatException e) {
    System.out.println("not a number");
}
System.out.println("continue");''','not a number\ncontinue\n',['try 放可能无法完成的操作','catch 处理指定种类的异常','处理后继续执行后面的语句'],diagram='exception')
scene(c,'11-2','用明确规则拒绝不合理的值','''程序自己的规则也可能要求拒绝某个值。这里的方法接收成绩，如果小于零或者大于一百，就用 throw 报告参数不合适，后面的正常返回不会继续执行。
IllegalArgumentException 这个名字表示传入的参数不符合要求。完整示例在调用处尝试交入一百二十，并用对应的 catch 显示 bad score。换成八十，就会正常返回八十。
并不是每一个判断都必须写成异常。普通的“及格还是不及格”，用 if 分支表达就足够。这里想强调的是，方法不能按约定完成任务时，应当清楚报告失败，调用的一方再根据需要处理。暂时不展开所有异常类别，只要看懂从报告问题到处理问题的这条路线，就能阅读很多入门程序。''',r'''static int requireScore(int value) {
    if (value < 0 || value > 100) {
        throw new IllegalArgumentException("bad score");
    }
    return value;
}''','bad score\n',['范围外的成绩不符合方法约定','throw 报告这次操作无法完成','调用处 catch 对应异常并提示'],diagram='validation',runner='try { System.out.println(requireScore(120)); } catch (IllegalArgumentException e) { System.out.println(e.getMessage()); }')
scene(c,'11-q','课堂练习：异常改变哪一步','''请沿着这段程序跟踪显示的字母。先显示 A，然后尝试把 abc 转成整数，后面还写着显示 B。catch 里面显示 C，整个处理结构之后显示 D。
如果转换抛出了刚才学习的异常，A、B、C、D 哪些会真正显示，顺序又是什么？注意，catch 并不是无论成功失败都执行的一段代码，转换失败以后也不会自动回去补做 try 里面剩下的语句。
给你四秒，在纸上画出正常向下和跳到 catch 的两条路线，选出本次实际走过的那一条。''',r'''try {
    System.out.print("A ");
    Integer.parseInt("abc");
    System.out.print("B ");
} catch (NumberFormatException e) {
    System.out.print("C ");
}
System.out.println("D");''','A C D\n',['先执行转换前的显示','失败时跳到对应 catch','再执行整个结构之后的语句'],kind='question')
scene(c,'11-a','答案：失败路线跳过 B','''原题显示 A、C、D。A 在转换之前已经显示。转换失败后跳到 catch，try 里面剩下的 B 被跳过，显示 C，再执行结构后面的 D。
画面把转换内容改成正常的八十，用另一条路线做对照。这次转换成功，继续执行 B，不进入 catch，所以显示 A、B、D。两种情况放在一起，更容易看清 catch 的作用。
不要只记住一串字母，要记住执行过程：先按顺序做事，发生指定异常时转去相应处理，处理后继续往下。以后遇到错误信息，先找到失败的操作和具体原因，再决定怎样修正数据或者处理失败，比把所有问题都藏在一个空的 catch 里面更有帮助。''',r'''try {
    System.out.print("A ");
    Integer.parseInt("80");
    System.out.print("B ");
} catch (NumberFormatException e) {
    System.out.print("C ");
}
System.out.println("D");''','A B D\n',['原题失败路线：A → C → D','修正版成功路线：A → B → D','catch 只在匹配的异常发生时执行'],diagram='exception-routes')

c=chapter('12','综合回顾','Review',2)
scene(c,'12-1','把程序拆成看得懂的小步骤','''现在回到开头的目标。你已经从第一行显示文字出发，学会给数据起名字，区分整数、文字和真假，再用表达式计算，用输入输出和用户交流。
遇到选择，用条件和分支；重复处理，用循环；保存一组同类数据，用数组或列表；把一段步骤重复使用，就写成方法。相关数据和操作可以放进类，再创建具体对象。根据名字找信息可以用映射表，遇到无法正常完成的操作，可以明确报告并处理异常。
这些内容不用一次全部背熟。读程序时先问：目前保存了什么数据？下一条语句修改了谁？判断会走哪条路？循环何时结束？如果涉及对象，再画出变量通向哪一份记录。每次只追踪一个具体变化，就能把长一点的程序拆成已经认识的小步骤。''',notes=['数据：变量、类型与表达式','流程：输入输出、分支与循环','组织：数组、方法与对象','工具：集合与异常处理'],diagram='recap')
scene(c,'12-2','独立完成一个成绩统计程序','''最后把几个熟悉的动作连成一个成绩统计程序。数组里是六十、八十、一百。循环从位置零开始，逐个把成绩加到 total，得到二百四十。总和先转成 double 再除以数量，所以 average 保存八十点零。
level 是完整程序中准备好的小方法：平均分至少六十，返回 pass，否则返回 retry。主方法负责准备数据、计算结果和显示，判断文字交给单独的方法完成。每一小段都在做一件能说明白的事。
课后先不看答案，自己输入这段程序，再改动三门成绩，预测新结果。接着试着添加最低分、最高分，或者把输入交给用户。今天的目标是让你能写出并解释第一批小程序。熟悉这些基础以后，再继续学习更完整的类设计、文件和其他常用工具。先把眼前的小程序亲手运行起来，下一步就有了牢固的起点。''',r'''int[] scores = {60, 80, 100};
int total = 0;
for (int i = 0; i < scores.length; i++) {
    total += scores[i];
}
double average = (double) total / scores.length;
System.out.println("average=" + average);
System.out.println(level(average));''','average=80.0\npass\n',['逐项相加得到总分 240','转成 double 后计算平均分','level 方法把平均分变成判断结果'],diagram='final',members='static String level(double average) { if (average >= 60) { return "pass"; } else { return "retry"; } }')
