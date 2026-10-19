from author import chapter,scene

c=chapter('09','结构体','Structures',5)
scene(c,'09-1','把相关信息放在一起', '''数组适合放一组同类型数据，但一位同学的信息可能同时有姓名和成绩。结构体可以把这些相关字段组合起来，形成一条更完整的记录。
屏幕先定义 Student 这个结构，里面有十六个字符位置的 name 和一个整数 score。注意定义结束的大括号后面有分号。接下来声明一位同学 s，并按字段顺序给出姓名 Ana 和成绩八十。
访问某个字段，用变量名加点，再写字段名。所以 s 点 name 表示这位同学的姓名，s 点 score 表示他的成绩。输出就能把两者放在同一行。结构体不要求里面的字段类型相同，但它们应该在含义上属于同一个对象。这样读代码时，不必靠几个平行数组猜哪份姓名对应哪份成绩，关系可以直接写在数据组织里。''',r'''struct Student {
    char name[16];
    int score;
};
struct Student s = {"Ana", 80};
printf("%s %d\n", s.name, s.score);''','Ana 80\n'.replace('\\n','\n'),['结构体组合相关字段','定义结束后有分号','变量.字段 访问数据'],diagram='struct')
scene(c,'09-2','结构体也可以组成数组', '''一个结构体保存一位同学，多位同学就可以放进结构体数组。屏幕上有两条记录，第一位 Ana 八十分，第二位 Ben 九十分。
我们用循环访问编号零和一。students 的第 i 项先找到某一条记录，再用点 name、点 score 取出这位同学的字段。结果按顺序显示两个人的信息。
这里没有新的访问魔法，只是把已经学过的两步连起来：方括号选哪一位，点号选哪一项信息。给第一位同学加五分，也只是把编号零的 score 更新一下。把一个新需求拆回熟悉的小动作，是学习编程很有用的方法。先分清自己现在处理的是整条记录，还是其中某个字段，再选择对应写法。''',r'''struct Student { char name[16]; int score; };
struct Student students[2] = {{"Ana", 80}, {"Ben", 90}};
for (int i = 0; i < 2; i++) {
    printf("%s %d\n", students[i].name, students[i].score);
}''','Ana 80\nBen 90\n'.replace('\\n','\n'),['数组选记录，点号选字段','students[0] 是第一位','姓名与成绩放在同一条记录'],diagram='struct-array')
STRUCT_PTR=r'''#include <stdio.h>
struct Student { char name[16]; int score; };
void bonus(struct Student *p) {
    p->score += 5;
}
int main(void) {
    struct Student s = {"Ana", 80};
    bonus(&s);
    printf("%s %d\n", s.name, s.score);
    return 0;
}'''
scene(c,'09-3','通过结构体指针修改字段', '''如果函数需要修改一位同学的原始成绩，也可以把整个结构体的地址交进去。参数 p 是指向 Student 记录的指针，调用时传入 s 的地址。
对于结构体指针，箭头符号用来访问所指记录的字段。所以 p 箭头 score，表示沿着 p 找到这位同学，再访问他的成绩。这里加五后，main 中的 s 也变成八十五。
点号和箭头怎么选，可以看手里拿的是什么：直接拿到结构体变量，用点号；拿到指向结构体的指针，用箭头。箭头访问也可以展开成先对 p 解引用，再访问字段，不过直接写箭头通常更清楚。所有指针访问仍然要保证目标有效。本例的 s 一直在 main 里，函数返回前都还存在，所以沿地址修改有明确对象。''',STRUCT_PTR,'Ana 85\n'.replace('\\n','\n'),['传入结构体的地址','变量用点号，指针用箭头','原来的记录被修改'],diagram='struct-pointer')
scene(c,'09-q','课堂练习：复制记录以后', '''现在结构体 a 保存 Ana 和八十分，随后把整条记录复制给 b。接下来只把 b 的成绩改成九十分。最后 a 和 b 的成绩分别是多少？
请留意这两个变量本身都是结构体，不是指向同一条记录的两个指针。这个结构体的姓名数组和成绩都直接放在记录里，赋值会复制这些字段的内容。
你可以回想普通整数变量的那一题。先复制，再只修改副本，会不会自动把原件也改掉？四秒之后，我们把结构体赋值和通过地址修改再区分一次。''',r'''struct Student { char name[16]; int score; };
struct Student a = {"Ana", 80};
struct Student b = a;
b.score = 90;
printf("%d %d\n", a.score, b.score);''','80 90\n'.replace('\\n','\n'),['a、b 是两条独立记录','这次没有共享目标的指针','只修改 b.score'],kind='question')
scene(c,'09-a','答案：原记录与副本分别保存', '''答案是八十和九十。b 等于 a 时，复制了这个结构体里面的字段内容。后面修改 b 的成绩，只影响 b，不影响 a。
这里姓名数组直接属于结构体，所以姓名内容也随记录一起复制。先不要把这个结论随意推广到所有复杂结构：如果某个字段保存的是指针，复制那个字段时复制的是地址，仍需要追踪它指向谁。本课的 Student 使用固定字符数组和整数，关系比较直接。
到现在，我们已经会用变量保存一个数字，用数组保存一组同类型数据，用结构体把不同但相关的信息合起来。看到一个需求时，不一定马上开始写循环，也可以先想数据应该怎样组织。把姓名和成绩的关系表达清楚，后面的计算与输出就会少一些容易混淆的对应关系。''',r'''struct Student { char name[16]; int score; };
struct Student a = {"Ana", 80};
struct Student b = a;
b.score = 90;
printf("%d %d\n", a.score, b.score);''','80 90\n'.replace('\\n','\n'),['a.score 保留 80','b.score 变成 90','要分清字段是数据还是地址'],diagram='struct-copy')

c=chapter('10','文件操作','Files',6)
WRITE=r'''#include <stdio.h>
int main(void) {
    FILE *fp = fopen("scores.txt", "w");
    if (fp == NULL) { printf("open failed\n"); return 1; }
    if (fprintf(fp, "%d\n", 80) < 0) { fclose(fp); return 1; }
    if (fclose(fp) != 0) return 1;
    printf("saved\n");
    return 0;
}'''
scene(c,'10-1','打开、写入、关闭', '''程序结束以后，普通变量里的成绩不会自动变成可以下次再读的文件。想保存到磁盘，需要明确打开一个文件，向它写内容，最后关闭。
fopen 接收文件名和打开方式，返回一个文件使用凭据，类型写作 FILE 星号。我们把它保存在 fp 中，后面读写时传给相应函数。如果返回 NULL，表示没有成功打开，不能继续把它当成有效文件。
这里的 w 表示为写入打开。它会创建不存在的文件；如果同名文件已经存在，会清空原有内容再写，所以使用前要确认这是你要的行为。fprintf 很像 printf，只是前面多了文件对象参数。它把八十和换行写入 scores 点 txt。最后 fclose 关闭文件并检查结果。屏幕上的 saved 是给人看的确认消息，文件里真正保存的是八十这一行。''',r'''FILE *fp = fopen("scores.txt", "w");
if (fp == NULL) { printf("open failed\n"); return 1; }
if (fprintf(fp, "%d\n", 80) < 0) {
    fclose(fp); return 1;
}
if (fclose(fp) != 0) return 1;
printf("saved\n");''','saved\n'.replace('\\n','\n'),['w：创建或清空后写入','先检查 fp 是否为 NULL','文件内容：80 和换行'],diagram='file-write',full=WRITE,expectedFiles={'scores.txt':'80\n'.replace('\\n','\n')})
READ=r'''#include <stdio.h>
int main(void) {
    FILE *fp = fopen("scores.txt", "r");
    if (fp == NULL) return 1;
    int score = 0;
    int read = fscanf(fp, "%d", &score);
    int closed = fclose(fp);
    if (read != 1 || closed != 0) return 1;
    printf("%d\n", score);
    return 0;
}'''
scene(c,'10-2','从文件里读回一个成绩', '''再打开同一个文件，这一次方式写成 r，表示读取已有内容。文件中的八十是一段数字文字，fscanf 按整数格式把它读回 score。
你会发现，fscanf 和 scanf 的形式很相似：前面多一个文件对象，后面仍然需要说明格式和变量地址。它也会返回成功赋值的项目数量。本例想读一个整数，就检查结果是不是一。
无论读取结果是否符合要求，已经打开的文件都应该安排关闭。所以这里先保存读取结果，再关闭文件，最后统一检查；成功后才显示成绩。相对文件名是相对于程序的工作目录，不一定就是源代码所在目录。练习时，把要读的文件放在约定的运行目录，并核对文件内容，能减少“明明存在却找不到”的困惑。''',r'''FILE *fp = fopen("scores.txt", "r");
if (fp == NULL) return 1;
int score = 0;
int read = fscanf(fp, "%d", &score);
int closed = fclose(fp);
if (read != 1 || closed != 0) return 1;
printf("%d\n", score);''','80\n'.replace('\\n','\n'),['r：读取已有文件','fscanf 也检查成功项数','本例文件内容：80'],diagram='file-read',full=READ,files={'scores.txt':'80\n'.replace('\\n','\n')})
APPEND=r'''#include <stdio.h>
int main(void) {
    FILE *fp = fopen("scores.txt", "a");
    if (fp == NULL) return 1;
    if (fprintf(fp, "%d\n", 90) < 0) { fclose(fp); return 1; }
    if (fclose(fp) != 0) return 1;
    printf("appended\n");
    return 0;
}'''
scene(c,'10-3','保留旧内容，再追加一行', '''如果文件已经有八十，想在后面再保存九十，就不能用刚才会清空文件的 w。可以使用 a，表示追加写入，新的内容会放到文件末尾。
屏幕这段程序打开已有的 scores 文件，追加九十和换行，然后关闭。完成后，文件从原来一行八十，变成第一行八十、第二行九十。程序显示 appended，表示这次追加步骤完成。
把 r、w、a 和具体任务联系起来：r 取出已有内容，w 准备一份新的写入内容，a 在旧内容后继续加。不要把打开方式当成随手抄的一个字母，它直接决定对已有资料做什么。我们这里练习的是简单文本文件，后面还可以学习逐行读取、完整格式校验，以及更复杂的文件结构；先把这三个基本动作写对就很好。''',r'''FILE *fp = fopen("scores.txt", "a");
if (fp == NULL) return 1;
if (fprintf(fp, "%d\n", 90) < 0) {
    fclose(fp); return 1;
}
if (fclose(fp) != 0) return 1;
printf("appended\n");''','appended\n'.replace('\\n','\n'),['a：在文件末尾追加','原有 80 得到保留','最终文件两行：80、90'],diagram='file-append',full=APPEND,files={'scores.txt':'80\n'.replace('\\n','\n')},expectedFiles={'scores.txt':'80\n90\n'.replace('\\n','\n')})
FAIL=r'''#include <stdio.h>
int main(void) {
    FILE *fp = fopen("not_created_dir/scores.txt", "r");
    if (fp == NULL) { printf("open failed\n"); return 1; }
    if (fclose(fp) != 0) return 1;
    return 0;
}'''
scene(c,'10-4','失败也是正常的执行情况', '''文件名写错、文件不存在，或者没有相应权限，都可能导致打开失败。这不是只会发生在新手身上的特殊情况，而是程序应该预先考虑的一条路径。
屏幕故意读取一个没有创建的目录里的文件，fopen 返回空指针，程序显示 open failed 并结束。它没有继续读，也没有对这个空目标执行关闭。
读写成功与否也要检查。写入函数出现负值，或者关闭文件返回错误，都不能仅凭前面已经执行到这一行就认定保存一定成功。今天的例子把必要检查保留在完整程序里，画面只展示当前要理解的一小段。这样既不会让初学者一次盯着几十行，也不会把真实程序里的失败情况藏起来。以后遇到更复杂需求，再在这些清楚的分支上扩展提示和恢复策略。''',r'''FILE *fp = fopen("not_created_dir/scores.txt", "r");
if (fp == NULL) {
    printf("open failed\n");
    return 1;
}
if (fclose(fp) != 0) return 1;''','open failed\n'.replace('\\n','\n'),['目标文件和目录尚未创建','打开失败不继续读写','读、写、关闭都有结果'],diagram='file-read',full=FAIL,runs=[dict(stdin='',output='open failed\n'.replace('\\n','\n'),exitCode=1)])
scene(c,'10-q','课堂练习：覆盖还是追加', '''文件已经保存了八十分，接下来要把九十分接在后面，保留旧记录。屏幕上现在用的是 w，它能保留旧记录吗？应该改成 r、w 还是 a 打开？
请按打开方式的含义判断，不用去猜某个编辑器是否给你保留了副本。程序要明确向文件系统提出哪一种请求，就会影响现有文件内容。
四秒之后，我们使用正确方式执行一次，并同时检查程序结果和文件本身。看见一条成功提示还不够，也要确认保存下来的内容确实符合需求。''',r'''FILE *fp = fopen("scores.txt", "w");
if (fp == NULL) return 1;
if (fprintf(fp, "%d\n", 90) < 0) {
    fclose(fp); return 1;
}
if (fclose(fp) != 0) return 1;
printf("written\n");''','written\n'.replace('\\n','\n'),['需求：保留旧的 80','再写入新成绩 90','r、w、a 选择哪一个'],kind='question',full=APPEND.replace('"a"','"w"').replace('appended','written'),files={'scores.txt':'80\n'.replace('\\n','\n')},expectedFiles={'scores.txt':'90\n'.replace('\\n','\n')})
scene(c,'10-a','答案：追加使用 a', '''应该使用 a。原文件里的八十得到保留，新写入的九十追加在后面。我们既核对了程序显示 appended，也实际核对了文件现在有八十和九十两行。
如果改成 w，成功打开原文件时就会清空旧内容，随后写入九十，原来的八十不会因为它也是一份成绩就自动留下。r 则是为了读取，不符合这次写入的目的。
这道题也把整个程序的思路收了回来：先明确需求，选合适的数据和操作，检查是否成功，再验证最终结果。文件是一个特别容易看见后果的地方，打开模式必须认真选择。现在你可以把一位同学的输入、成绩判断和保存操作连起来，再逐步扩展为多位同学的记录。不要一开始就追求很大的系统，先让最小的一条路径可靠地工作。''',r'''FILE *fp = fopen("scores.txt", "a");
if (fp == NULL) return 1;
if (fprintf(fp, "%d\n", 90) < 0) {
    fclose(fp); return 1;
}
if (fclose(fp) != 0) return 1;
printf("appended\n");''','appended\n'.replace('\\n','\n'),['a：保留并追加','w：清空后写入','核对文件内容，不只看提示'],diagram='file-append',full=APPEND,files={'scores.txt':'80\n'.replace('\\n','\n')},expectedFiles={'scores.txt':'80\n90\n'.replace('\\n','\n')})

c=chapter('11','综合应用与回顾','Review',3)
INTEGRATED=r'''#include <stdio.h>
struct Student { char name[16]; int score; };
int passed(int score) { return score >= 60; }
int main(void) {
    struct Student students[2] = {{"Ana", 80}, {"Ben", 59}};
    FILE *fp = fopen("report.txt", "w");
    if (fp == NULL) return 1;
    for (int i = 0; i < 2; i++) {
        int ok = passed(students[i].score);
        printf("%s %d\n", students[i].name, ok);
        if (fprintf(fp, "%s %d\n", students[i].name, ok) < 0) {
            fclose(fp); return 1;
        }
    }
    if (fclose(fp) != 0) return 1;
    return 0;
}'''
scene(c,'11-1','把已经学过的动作连起来', '''最后把几个熟悉的动作连起来。结构体描述一位同学，结构体数组保存两位同学，循环依次取出每条记录，passed 函数根据六十分规则交回判断结果，再把姓名和结果显示出来。
完整配套程序还会把同样的结果写进 report 点 txt，并检查打开、写入和关闭。画面先只展示处理记录的核心几行，不要求你在最后一分钟突然读懂一大页代码。你可以把每一步指回前面的章节：哪个是数据，哪个是重复动作，哪个是判断工具，结果最后到哪里。
程序显示 Ana 对应一，Ben 对应零。这不是一种全新的技巧，而是用清楚的数据关系，把已经练过的小步骤组装起来。自己练习时，可以先只处理一位同学，确认结果后再加数组；先只输出到屏幕，确认内容后再加文件。一次增加一个能验证的小功能，比同时堆上所有代码更容易找到问题。''',r'''for (int i = 0; i < 2; i++) {
    int ok = passed(students[i].score);
    printf("%s %d\n", students[i].name, ok);
}''','Ana 1\nBen 0\n'.replace('\\n','\n'),['结构体数组组织记录','循环与函数处理每一位','完整程序同时写入文件'],diagram='roadmap',full=INTEGRATED,expectedFiles={'report.txt':'Ana 1\nBen 0\n'.replace('\\n','\n')})
scene(c,'11-2','从看懂走向自己写出来', '''回顾这一小时，我们先用变量和类型表达数据，用运算符算出结果，用输入输出和使用者交换信息。然后用分支做选择，用循环重复步骤，用数组和字符串管理一组内容。
函数帮我们整理步骤，递归把同类问题逐步缩小，指针让我们按地址访问原数据，结构体组合相关信息，文件把结果保存下来。你现在可以把一个小程序拆成这些熟悉的部分，再逐项解释它为什么这样运行。
课后建议按三个动作练习：先预测一个例子的输出，再真正运行，最后只改一个条件或一份输入，看变化是否符合自己的判断。优先把输入检查、循环边界、字符串结束标记和有效指针这几个点练扎实。交付资料里有完整示例和课堂题，可以从最短的开始逐个修改。学习编程不靠一次把所有符号背熟，而是反复完成“提出一个小需求、写出步骤、验证结果”。我们下一次再从这些已经看得见的基础上往前走。''',notes=['先预测，再运行，再小改动','重点检查输入、边界与地址','从一个能验证的小功能开始'],diagram='roadmap')
