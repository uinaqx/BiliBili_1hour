from author import chapter,scene
c=chapter('07','数组与字符串','Arrays and Strings',7)
scene(c,'07-1','把一组成绩放在一起','''如果有三份成绩，不必为它们分别起 score 一、score 二、score 三这样的名字，可以用数组保存同一种类型的一组值。int 后面的方括号表示这里准备保存一组整数。
大括号里依次放六十、八十、一百。要读取某一项，在数组名字后面写方括号和位置编号。特别注意，第一项的编号是零，所以 scores 方括号零读到六十。
位置编号也叫下标。它不是成绩本身，而是告诉程序这次要访问哪一个位置。给 scores 方括号一赋八十五，改的是第二项，其他项不会跟着变化。先画出几个并排的格子，把零、一、二写在上方，再把成绩写在格子里面，就能分清位置和内容。''',r'''int[] scores = {60, 80, 100};
System.out.println(scores[0]);
scores[1] = 85;
System.out.println(scores[1]);''','60\n85\n',['数组保存同种类型的一组值','第一项下标是 0','下标指定位置，赋值修改该项'],diagram='array')
scene(c,'07-2','数组长度和最后一个位置','''数组的 length 表示里面有多少项。本例有三项，所以长度是三。但位置从零开始，合法下标依次是零、一、二，最后一项并不是编号三。
因此最后一项可以用长度减一来取得，读取结果是一百。数组一旦创建，这份数组的长度就固定了；修改其中的分数，并不会凭空多出第四个位置。
如果提前知道有三个位置，也可以用 new int 方括号三创建它，再逐项填写。新建的整数数组初始元素为零，但这不等于每一个方法里的普通局部变量也会自动得到可读取的零值。先把本页的两件事分清：length 说明数量，下标说明位置。访问前要确认位置在这份数组的有效范围内。''',r'''int[] scores = {60, 80, 100};
System.out.println(scores.length);
System.out.println(scores[scores.length - 1]);
int[] empty = new int[3];
System.out.println(empty[0]);''','3\n100\n0\n',['长度是数量：3','合法下标：0、1、2','最后一项下标：length - 1'],diagram='array-length')
scene(c,'07-3','用循环逐项完成统计','''有了数组，循环就能沿着位置逐项读取。i 从零开始，只要还小于数组长度，就读取 scores 方括号 i，把这一项加到 total 中。
这里用小于长度，正好覆盖零到长度减一，不会访问不存在的下一项。总和是二百四十，平均分用小数除法计算，得到八十点零。前面学过的变量、循环和除法，现在就在完成同一个小任务。
如果只想依次读每一项，不关心位置编号，也可以使用增强 for，写成 for 括号 int score 冒号 scores。它会依次把每个整数值交给 score。配套例子还提供这种写法。本页先保留下标版本，因为它最能帮助我们看清循环范围和数组有效位置之间的关系。''',r'''int[] scores = {60, 80, 100};
int total = 0;
for (int i = 0; i < scores.length; i++) {
    total += scores[i];
}
double average = total / 3.0;
System.out.println(total);
System.out.println(average);''','240\n80.0\n',['i 从 0 到 length - 1','逐项读取，再累加','平均分使用小数计算'],diagram='array-sum')
scene(c,'07-4','读取文字的长度与一段内容','''字符串也提供了一些现成操作。name 点 length 括号，取得本页这段英文姓名的长度，Ana 得到三。charAt 括号零，读取第一个位置的字符，得到大写 A。
substring 括号一逗号三，取得从位置一开始、到位置三之前的那一段，所以结果是 n 和 a。右边界不包含在结果里，这个范围规则需要特别看清。
这里有一个写法差别：数组长度用 length，不带括号；字符串取得长度用 length 括号。后者是在调用字符串提供的方法。我们先用简单英文内容练习这些操作，复杂文字的字符表示留到后续学习，不把这个长度直接当成所有文字里人眼看到的字符个数。''',r'''String name = "Ana";
System.out.println(name.length());
System.out.println(name.charAt(0));
System.out.println(name.substring(1, 3));''','3\nA\nna\n',['字符串 length() 带括号','charAt 从下标 0 开始','substring 包含左端，不包含右端'],diagram='string')
scene(c,'07-5','比较文字内容，接住新结果','''比较两段文字内容是否相同，可以调用 equals。name 保存 Ana，name 点 equals 括号 Ana 的结果就是 true。不要把前面比较两个整数的双等号，直接当成比较字符串内容的通用办法。
字符串还可以交回大小写转换后的结果。toUpperCase 返回全部转成大写的文字，我们把它保存进 upper，得到 ANA。原来的 name 仍然显示 Ana，因为这次操作没有把原字符串内容原地改掉。
对初学者来说，先记住一个很实用的检查方法：调用一个操作以后，问它是改变已有对象，还是交回一个新结果。如果它交回结果而我们没有接住，后面继续读取原变量，可能仍然看到原来的内容。本页正好用两个变量把这种差别摆出来。''',r'''String name = "Ana";
System.out.println(name.equals("Ana"));
String upper = name.toUpperCase();
System.out.println(name);
System.out.println(upper);''','true\nAna\nANA\n',['文字内容比较使用 equals','转换操作交回新字符串','name 保持 Ana，upper 保存 ANA'],diagram='string-result')
scene(c,'07-q','课堂练习：长度能当最后下标吗','''scores 保存三份成绩。现在用 scores 点 length 作为下标去取值，会得到最后一项一百吗？还是会遇到问题？
先写出这份数组的长度，再写出从零开始的全部合法位置。把这两组数摆在一起，就不容易凭直觉把“共有三项”误解成“最后编号为三”。
给你四秒。这道题的写法可以通过编译，所以还需要继续判断运行时实际访问的位置是否存在。我们会把结果明确标成运行时异常，再给出只改一个位置的正确版本。''',r'''int[] scores = {60, 80, 100};
System.out.println(scores[scores.length]);''','运行时异常：ArrayIndexOutOfBoundsException',['length 是 3','合法位置只有 0、1、2','区分能编译与访问有效'],kind='question',verify='runtime_error',diagnostic='ArrayIndexOutOfBoundsException')
scene(c,'07-a','答案：最后一个下标要减一','''原题运行时会发生数组下标越界异常，因为试图访问不存在的第四个位置。它不是读到一个自动补出来的零，也不是返回最后一项。
把下标改成 scores 点 length 减一，本例就是二，才读到最后的一百。这个写法的前提是数组至少有一项；如果一项都没有，就需要先检查长度，不能继续套用最后一项的访问方式。
我们现在只处理这份明确有三个元素的数组，所以结果确定是一百。以后遇到一组数据，先确认有没有内容，再确认要访问的位置，最后才读取数据。这个顺序比先访问、出了异常再猜哪里不对，更能帮助你写出清楚的小程序。''',r'''int[] scores = {60, 80, 100};
if (scores.length > 0) {
    int last = scores.length - 1;
    System.out.println(scores[last]);
}''','100\n',['先确认数组不是空的','最后一项位于 length - 1','本例读取下标 2，得到 100'],diagram='array-length')
c=chapter('08','方法','Methods',6)
scene(c,'08-1','给一组步骤起名字','''假设程序里多次需要显示同一句欢迎语。可以把这条操作放进一个方法，给它起名 greet。后面写 greet 括号，就是调用它，进入方法里面完成那组步骤。
本页的方法写在 Main 类里面、main 方法外面，完整文件会显示这个位置关系。定义方法时说明步骤是什么，遇到调用时才真正执行，所以不会因为我们写了定义，就先自动显示一遍。
这里 static 暂时配合 Main 里的调用方式使用，表示方法属于这个类，不必先建立一个 Main 对象。void 表示它不交回一个需要接收的计算值。本页只做显示动作。先把方法理解成一个有名字的小任务，下一页再让它接收数据、交回结果。''',r'''static void greet() {
    System.out.println("Hello!");
}''','Hello!\nHello!\n',['方法把一组步骤组织起来','定义不等于立即执行','写 greet() 才发起调用'],diagram='method',runner='greet(); greet();')
scene(c,'08-2','交入参数，再交回结果','''add 这个方法负责把两个整数相加。括号里的 a 和 b 是本次调用接收数据的位置，前面的 int 说明它们接收整数。
调用 add 括号三逗号五时，三交给 a，五交给 b。return 把算出的八交回调用位置，我们再把它保存到 result，或者直接交给显示操作。方法名前面的 int 表示这个方法会返回整数，和上一页的 void 不同。
参数名字可以帮助方法内部表达步骤，不要求调用者也必须使用同样名字的变量。关键是传入的顺序、数量和类型符合要求。把箭头画成“调用者交入三和五，方法计算，再交回八”，就能看清数据怎样经过这个小任务，而不是把函数名字当成凭空得到答案的词。''',r'''static int add(int a, int b) {
    return a + b;
}''','8\n',['参数接收本次调用的数据','返回类型 int 表示交回整数','return 把结果交回调用位置'],diagram='method-add',runner='int result=add(3,5); System.out.println(result);')
scene(c,'08-3','把判断规则放进方法','''方法不只会做算术，也可以把一条判断规则集中写清楚。isPassed 接收一个成绩，返回这个成绩是否至少达到六十。
返回类型是 boolean，所以调用结果是真或假。给它五十九，得到 false；给它六十，得到 true。如果程序里多个地方都需要及格规则，调用同一个方法，就不用在不同位置反复手抄条件。
return 会结束这一次方法调用，把结果交回去；它不是让所有程序都立刻停止。接收到结果以后，main 还可以继续显示、作条件判断，或者执行下一次调用。把常用规则交给一个小方法，也方便以后只在一个清楚的位置调整规则，再重新检查各处调用是否得到合适的结果。''',r'''static boolean isPassed(int score) {
    return score >= 60;
}''','false\ntrue\n',['方法也可以返回判断结果','同一规则集中表达','return 结束本次方法调用'],diagram='method-check',runner='System.out.println(isPassed(59)); System.out.println(isPassed(60));')
scene(c,'08-4','变量有自己的使用范围','''再回头看看大括号对名字的影响。bonus 在 if 的大括号里面声明，只能在它所属的有效范围里使用。走出这组大括号以后，外面的显示语句不能直接继续使用这个局部名字。
所以本页会编译失败。不是条件明明成立却不肯执行，而是编译器先发现外面这一处 bonus 没有可用的声明，整个程序还不能开始运行。
如果后面确实也要用到它，就应该在合适的外层先声明并准备初值，再让里面的分支按需要修改。不要因为看到一个地方出现过名字，就认为整个文件里任何位置都能使用。方法的参数和局部变量，也要结合它们所属的方法和大括号范围来理解。''',r'''int score = 80;
if (score >= 60) {
    int bonus = 5;
    System.out.println(score + bonus);
}
System.out.println(bonus);''','编译失败：bonus 在外层语句中不可用',['局部名字有使用范围','if 内声明的 bonus 不供外层使用','先通过编译，再讨论运行路线'],diagram='scope',verify='compile_error',diagnostic='cannot find symbol')
Q=r'''static void addFive(int value) {
    value += 5;
}
public static void main(String[] args) {
    int score = 80;
    addFive(score);
    System.out.println(score);
}'''
scene(c,'08-q','课堂练习：外面的成绩变了吗','''score 是八十，交给 addFive 方法。方法内部给参数 value 加五，但没有把一个结果返回给调用者。方法结束后，外面的 score 会是八十还是八十五？
先把方法参数和调用者的整数变量画成两个位置。调用时把整数值交进去，是否就意味着方法内部给参数赋值，会自动改掉外面的那一个变量？
给你四秒。这里先只讨论整数值，不把后面对象的关系混进来。判断完以后，我们会用一个明确交回新值、再保存回原变量的版本完成真正的加分。''',Q,'80\n',['调用时传入整数的值','value 是方法自己的参数位置','观察是否把结果保存回 score'],kind='question',full='public class Main {\n'+Q+'\n}')
A=r'''static int addFive(int value) {
    return value + 5;
}
public static void main(String[] args) {
    int score = 80;
    score = addFive(score);
    System.out.println(score);
}'''
scene(c,'08-a','答案：交回新值，再保存回去','''原题显示八十。调用时，参数 value 得到一份整数值，方法内部把这个参数位置改成八十五，并没有自动给外面的 score 重新赋值。
修正版让方法返回 value 加五的结果，再由调用者写 score 等于这次调用结果，外面的成绩才明确更新为八十五。读取旧值、计算新值、交回结果、保存回去，这四个步骤都有对应位置。
Java的方法传参采用传值方式。遇到对象时，传递的值可以是对象引用，后面会再看它怎样影响对象内容。但参数本身都不是一个可以通过重新赋值就自动改绑调用者变量的神秘通道。今天先用整数把最基本的路线看懂。''',A,'85\n',['原题只修改方法内的整数参数','修正后返回 85','调用者明确保存新结果'],diagram='method-return',full='public class Main {\n'+A+'\n}')
c=chapter('09','类与对象','Classes and Objects',6)
PLAIN=r'''class Student {
    String name;
    int score;
    void show() {
        System.out.println(name + " " + score);
    }
}'''
scene(c,'09-1','把同一位学生的数据放在一起','''现在一位学生既有姓名，又有成绩。把这些相关数据和显示它们的方法放在同一个定义里，就可以用 class 声明一个 Student 类。
类说明这种记录由什么组成，对象则是一份实际建立出来的记录。Main 里面写 new Student，就创建一个学生对象，再通过变量 s 使用它。写 s 点 name 或 s 点 score，访问的是这一位学生对应的字段。
字段可以先理解成对象内部有名字的数据。show 则是操作这份数据的方法。调用 s 点 show，显示它自己的姓名和成绩。前面先分别学习变量、方法和使用范围，是为了让现在这组结构不再突然出现很多无法解释的词。类就是把有关联的东西组织到一起，让它们围绕同一个对象工作。''',PLAIN,'Ana 80\n',['类定义相关数据与操作','new Student 创建一个具体对象','s.show() 使用这份对象的数据'],diagram='class',placement='type',runner='Student s=new Student(); s.name="Ana"; s.score=80; s.show();')
scene(c,'09-2','两个对象各有一份成绩','''同一个 Student 类可以创建多个对象。a 使用一位学生对象，b 使用另一位。分别给它们准备姓名和成绩，修改 a 的分数，并不会自动把 b 的分数也改掉。
屏幕最后显示 a 是八十五，b 仍然是九十。这和前面整数变量分别保存值有相似的观察方法，但这里两份成绩分别放在各自的对象内部。
特别留意，建立了两份对象，是因为这里执行了两次 new Student。类型定义没有重新抄两遍，也能得到多份不同的状态。以后你会看到很多同一种类的对象放进集合里，每一份都按同样规则使用，又保存各自的信息。先把类作为说明、对象作为实际记录的关系分清，就能继续理解创建时的准备工作。''',r'''Student a = new Student();
Student b = new Student();
a.name = "Ana"; a.score = 80;
b.name = "Bo"; b.score = 90;
a.score = 85;
System.out.println(a.score + " " + b.score);''','85 90\n',['两次 new，创建两个对象','对象内部各有自己的字段','只修改 a，不会自动修改 b'],diagram='objects',context=PLAIN)
CONSTRUCT=r'''class Student {
    int score;
    Student(int initialScore) {
        score = initialScore;
    }
    int getScore() { return score; }
}'''
scene(c,'09-3','构造方法准备对象的初始值','''为了看清创建过程，暂时只保留成绩字段。Student 里面这个和类同名、没有返回类型的方法，是构造方法。new Student 括号八十，会在建立对象时把初始分数交进来。
构造方法把参数保存进对象的 score 字段，对象准备好以后，就可以通过 getScore 读取八十。不要在构造方法前面补一个 void，那会把它写成另一种普通方法，而不是这里的创建入口。
前面 Main 里的静态小方法可以直接通过类来使用；这里 getScore 通过某个 Student 对象调用，才知道读取的是哪位学生的成绩。它没有 static。先用“有没有需要操作的具体对象”理解这种差别，比把 static 机械地加在每一个方法前面更清楚。''',CONSTRUCT,'80\n',['构造方法与类同名，无返回类型','创建时交入初始成绩','getScore 通过具体对象读取字段'],diagram='construct',placement='type',runner='Student s=new Student(80); System.out.println(s.getScore());')
READY=r'''class Student {
    private int score;
    Student(int score) { this.score = score; }
    public int getScore() { return score; }
    public void setScore(int score) {
        this.score = score;
    }
}'''
scene(c,'09-4','通过公开方法使用内部数据','''把 score 字段前面加上 private，就不让类外代码直接随意读写它。外面通过公开的 getScore 和 setScore 使用成绩，类自己可以把读取或修改的规则集中放在这些入口里。
参数和字段现在都叫 score，所以 this 点 score 明确表示当前对象自己的字段，普通 score 表示这次传入的参数。this 可以先理解成“正在使用的这个对象”，不用把它当成所有对象共享的另一个分数。
还有一件重要的事：Student 变量保存的是使用对象的引用，可以先把它想成通向对象的入口。给另一个 Student 变量赋同一个引用，并不等于又执行了一次 new 创建新学生。下一道题就专门观察这两种情况，避免把复制整数值的印象不加区分地套到对象上。''',READY,'85\n',['private 字段通过公开方法使用','this.score 指当前对象的字段','对象变量保存通向对象的引用'],diagram='privacy',placement='type',runner='Student s=new Student(80); s.setScore(85); System.out.println(s.getScore());')
scene(c,'09-q','课堂练习：一个对象还是两个对象','''a 通过 new Student 创建了一位八十分的学生。下一行 b 等于 a，没有再写 new。通过 b 把成绩改成九十，最后通过 a 读取，会得到八十还是九十？
请数一数真正创建对象的操作执行了几次。两个变量名字出现了，是否就一定代表两位互不相关的学生？
给你四秒，试着画两个入口和它们通向的记录。我们这次不是给方法参数重新赋值，而是沿着 b 找到对象，再调用方法修改那份对象内部的数据。把“名字指向谁”和“对象里面有什么”分开，就能找出答案。''',r'''Student a = new Student(80);
Student b = a;
b.setScore(90);
System.out.println(a.getScore());''','90\n',['只执行了一次 new Student','a、b 通向同一个对象','setScore 修改对象内部的成绩'],kind='question',context=READY)
scene(c,'09-a','答案：两条入口对应同一份记录','''原题显示九十，因为 a 和 b 都使用同一个学生对象。通过 b 改掉内部的成绩，通过 a 读取时，自然也看到这份记录的新状态。
如果希望 b 使用独立记录，就要另外建立一个对象。修正版执行第二次 new，把 a 当前的八十分交给新对象，再修改 b，结果就是 a 仍然八十，b 是九十。
这也和方法传值的规则相容：复制一个对象引用，可以让两个位置都找到同一个对象；通过它修改对象内容会被其他入口观察到。它不等于复制整份对象，也不等于给参数另一个引用就能自动改绑外面的变量。先画清入口和记录，再逐步跟踪具体修改。''',r'''Student a = new Student(80);
Student b = new Student(a.getScore());
b.setScore(90);
System.out.println(a.getScore() + " " + b.getScore());''','80 90\n',['原题共享一份对象，所以读到 90','修正版再次 new，建立独立对象','修改 b 的成绩后，a 保持 80'],diagram='references',context=READY)
