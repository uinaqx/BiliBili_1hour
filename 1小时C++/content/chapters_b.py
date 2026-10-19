from author import chapter,scene

c=chapter('03','构造与析构','Construction and Destruction',6)
SCORE=r'''class Score {
    int value_;
public:
    Score(int n) : value_(n) {}
    int get() const { return value_; }
};'''
scene(c,'03-1','对象创建时准备初始状态', '''如果成绩对象一建立就应当有分数，可以用构造函数准备它。构造函数和类同名，没有返回类型，连 void 也不写。创建对象时，会调用与参数相匹配的构造函数。
这里创建 Score 对象时传入八十，冒号后面的 value 下划线括号 n，把成员直接初始化成这个值。因此对象创建完成后，就能读取八十，不需要再补一次 set。
把初始化和普通修改分开，会让对象状态更清楚。构造函数并不是 main 里随便调用的一段同名普通函数，而是建立对象过程中的一部分。你可以先把它看成新对象开始使用之前的准备步骤。下一页再让这个准备步骤有几种不同的入口。''',SCORE,'80\n'.replace('\\n','\n'),['构造函数与类同名','没有返回类型','创建对象时完成初始化'],diagram='construct',runner=r'''Score s(80); cout << s.get() << '\n';''')
OVER=r'''class Score {
    int value_;
public:
    Score() : value_(0) {}
    Score(int n) : value_(n) {}
    int get() const { return value_; }
};'''
scene(c,'03-2','构造函数可以有不同参数', '''一个类可以定义多个构造函数，只要参数列表能够区分。这里不传参数时，把成绩准备成零；传入一个整数时，就用这个整数作为初值。
所以 Score a 调用无参数版本，Score b 括号八十调用整数版本。两个对象读取出来分别是零和八十。它们的准备方式不同，但创建完成后仍然都是 Score 对象。
这就是构造函数重载。选择依据是传入参数的类型和数量，不是我们自己在对象建好之后再手工选择函数。另外，只要声明了带参数的构造函数，就不要假定编译器仍然会自动提供一个可用的无参数版本。如果你的类确实需要不传参数创建，就像屏幕这样明确写出合适的构造函数。''',OVER,'0 80\n'.replace('\\n','\n'),['不同参数，对应不同构造入口','无参数版本需要满足创建需求','不要把构造函数写上 void'],diagram='construct',runner=r'''Score a; Score b(80); cout << a.get() << " " << b.get() << '\n';''')
scene(c,'03-3','初始化列表先于函数体执行', '''构造函数参数后面的冒号，开始的是成员初始化列表。它负责直接建立成员的初始值，执行时间在构造函数体之前。
屏幕用一个 const 整数成员表示及格线。const 成员必须在合适的初始化阶段得到值，不能先让它创建好，再在函数体里普通赋值。因此这里写成 limit 下划线括号 n，随后进入的空大括号没有额外工作。
即使普通整数在构造函数体里赋值看起来也能工作，直接初始化仍然更能表达“对象一开始是什么”。当成员本身也是类对象时，初始化列表还决定调用它的哪个构造函数。稍后组合对象会专门展开这个过程。现在先记住两个阶段：先初始化成员，再执行构造函数体。''',r'''class Limit {
    const int limit_;
public:
    Limit(int n) : limit_(n) {}
    int get() const { return limit_; }
};''','60\n'.replace('\\n','\n'),['冒号后是初始化列表','先初始化成员，再执行函数体','const 成员在初始化时给值'],diagram='init',runner=r'''Limit rule(60); cout << rule.get() << '\n';''')
TRACE=r'''class Trace {
public:
    Trace() { cout << "begin "; }
    ~Trace() { cout << "end "; }
};'''
scene(c,'03-4','析构函数观察对象结束', '''析构函数在对象结束生命时做收尾，名字是波浪号加类名，也没有返回类型。本课只用一个打印例子观察它，不展开复杂资源管理。
main 中进入一个小代码块，创建 Trace 对象，先显示 begin。代码块结束时，这个局部对象被销毁，析构函数显示 end。随后 main 继续显示 after，所以三段文字按这个顺序出现。
普通局部对象不需要我们再手工调用一次析构函数。以后用标准库容器和资源管理类时，清理动作常会由它们的析构过程安排。今天先建立明确的时间线：构造负责开始，析构对应结束；对象离开作用域，会发生正常收尾，而不只是变量名字从屏幕上消失。''',TRACE,'begin end after\n'.replace('\\n','\n'),['~Trace 是析构函数','离开代码块时自动执行','本课只观察，不展开资源管理'],diagram='lifetime',runner=r'''{ Trace t; } cout << "after\n";''')
scene(c,'03-q','课堂练习：创建时传入什么', '''这个 Score 类只有一个需要整数参数的构造函数。现在 main 却写 Score s，没有交给它整数。它能不能自动把成绩设成零，然后顺利打印八十？
请只根据类已经提供的入口判断。不要因为成员是 int，就猜系统一定会帮我们补一个满足需求的创建方式。
四秒之后，我们会先解释编译结果，再给出一个明确交入初值的修正版。''',r'''Score s;
cout << s.get() << '\n';''','编译失败：没有可用的无参数构造函数。',notes=['类只提供 Score(int)','创建时没有传参数','先判断是否能构造对象'],kind='question',context=SCORE,verify='compile_error',diagnostic='no matching function')
scene(c,'03-a','答案：使用已有的整数构造入口', '''原程序不能编译，因为这个类没有可用的无参数构造函数。带参数版本并不同时意味着无参数版本也存在。
修正版写 Score s 括号八十，明确把八十交给已有构造函数，成员就被初始化成八十，读取结果也就是八十。如果需求是允许默认成绩零，也可以像前一页那样另外定义无参数构造函数。
建立对象和后面修改对象是不同阶段。先确定对象能否按这组参数建立，再讨论成员函数会返回什么。这个顺序在派生类构造、成员对象构造中同样适用：每一部分都需要一个实际可用的初始化方式。''',r'''Score s(80);
cout << s.get() << '\n';''','80\n'.replace('\\n','\n'),['原题缺少可用创建入口','显式传入 80','构造成功后再讨论使用'],diagram='construct',context=SCORE)

c=chapter('04','封装与共享','Encapsulation and Sharing',8)
THIS=r'''class Score {
    int value = 0;
public:
    void set(int value) { this->value = value; }
    int get() const { return value; }
};'''
scene(c,'04-1','this 指向当前对象', '''调用成员函数时，它需要知道正在操作哪一个对象。this 就是在普通非静态成员函数里，指向当前对象的指针。
屏幕故意让参数和成员都叫 value。set 函数里的普通名字 value 优先表示参数，而 this 箭头 value 明确表示当前对象的成员。这样就把传进来的八十，写到 s 自己的成员里。
调用 s 点 set 时，this 对应 s；如果换成另一个对象调用，就对应另一个对象。很多时候，成员名字不冲突，编译器允许省略 this，但概念上仍然是在访问当前对象。它不是一个所有对象共享的固定地址，而是这次成员调用所对应的对象位置。''',THIS,'80\n'.replace('\\n','\n'),['this：当前对象的指针','this->value 明确指向成员','同名参数与成员要区分'],diagram='this',runner=r'''Score s; s.set(80); cout << s.get() << '\n';''')
CONST=r'''class Score {
    int value_;
public:
    Score(int n) : value_(n) {}
    int get() const { return value_; }
    void set(int n) { value_ = n; }
};'''
scene(c,'04-2','const 成员函数表达只读操作', '''get 后面的 const，表示这个成员函数通过当前对象进行只读访问。它不能在函数体里普通地修改对象的非静态数据成员，也不能随意调用需要可修改对象的成员函数。
因此，即使对象本身声明成 const，也可以调用 get 读取成绩。屏幕创建一份只读的八十分记录，输出就是八十。set 没有这个只读承诺，不能拿同一个 const 对象去调用它修改成绩。
这能把“查询”和“修改”从接口上区分出来。const 成员函数不是承诺外界一切状态都不变，比如静态数据或指针所指的其他对象还需要分别判断。对于本课这个只保存整数的简单类，先抓住它保护当前对象普通成员的作用即可。''',r'''const Score s(80);
cout << s.get() << '\n';''','80\n'.replace('\\n','\n'),['查询函数可以标为 const','const 对象只能调用合适的只读接口','非 const set 不适用于此对象'],diagram='const',context=CONST)
COUNTER=r'''class Counter {
    static int count_;
public:
    Counter() { ++count_; }
    static int created() { return count_; }
};
int Counter::count_ = 0;'''
scene(c,'04-3','静态数据成员由类共享', '''普通成员属于每个对象，静态数据成员则不在每个对象里各放一份。本例的 count 下划线由 Counter 这个类共享，用来记录这些构造调用的累计次数。
构造函数每执行一次，就把同一个计数加一。我们先创建 a，再创建 b，最后读取共享计数，得到二。它不是 a 保存一、b 也各保存一之后再自动求和，而是两次都访问同一份计数。
在这里采用的C++十四写法中，类里面声明 static int count，类外再写一次带类名限定的定义并给零作为初值。不要把类外定义写成又声明了一个无关的普通变量。两个冒号把这个名字准确归到 Counter 类中。''',COUNTER,'2\n'.replace('\\n','\n'),['count_ 是类共享的一份数据','每次本例构造调用都加 1','C++14 中在类外给出定义'],diagram='static',runner=r'''Counter a, b; cout << Counter::created() << '\n';''')
scene(c,'04-4','静态成员函数没有当前对象', '''created 前面也写着 static，它是静态成员函数。调用时可以用类名加两个冒号，不必先指定某一个对象。
这种函数没有 this 指针，所以不能直接访问某个对象的普通成员。它可以直接访问类的静态成员，例如刚才那份共享计数。如果要处理普通成员，就需要另外得到一个具体对象，再通过那个对象访问。
屏幕先读取零，创建一个对象后再读取一，说明计数在整个类的使用过程中被共享。静态函数并不是自动拥有所有对象的数据，它只是一个归属于类、却不依赖隐含当前对象的函数。把有没有 this 这个问题弄清楚，普通成员函数和静态成员函数的边界就很容易判断。''',r'''cout << Counter::created() << " ";
Counter a;
cout << Counter::created() << '\n';''','0 1\n'.replace('\\n','\n'),['用 Counter::created() 调用','静态成员函数没有 this','普通成员仍需要具体对象'],diagram='static',context=COUNTER)
FRIEND=r'''class Score {
    int value_;
public:
    Score(int n) : value_(n) {}
    friend int inspect(const Score& s);
};
int inspect(const Score& s) { return s.value_; }'''
scene(c,'04-5','友元函数获得指定访问许可', '''有时一个普通函数需要参与某个类的紧密协作，但我们不想把数据向所有外部代码公开。这时可以在类中声明一个指定函数为 friend，也就是友元。
inspect 仍然是普通函数，不是 Score 的成员函数。它通过参数 s 得到要查看的对象，而不是使用成员函数隐含的 this。因为 Score 明确授予它友元权限，它可以直接读取私有的 value。
这个许可只给指定的友元，并不会让私有成员变成 public。调用时也不是 s 点 inspect，而是像普通函数一样写 inspect 括号 s。友元有明确用途，但不应该为了绕过所有接口限制而到处添加。先判断这种协作是否确实需要直接访问，再给出范围清楚的许可。''',FRIEND,'80\n'.replace('\\n','\n'),['friend 授权给指定函数','友元函数仍是普通函数','通过参数访问某个对象'],diagram='friend',runner=r'''Score s(80); cout << inspect(s) << '\n';''')
FRIEND_CLASS=r'''class Score {
    int value_ = 80;
    friend class Auditor;
};
class Auditor {
public:
    int read(const Score& s) const { return s.value_; }
};'''
scene(c,'04-6','友元类把许可给一组成员函数', '''如果协作需要由一个类的成员完成，也可以声明友元类。Score 把 Auditor 声明为友元后，Auditor 的成员函数就可以访问 Score 的私有成员。
屏幕上检查员对象通过 read 接收一份成绩记录，读取到八十。Score 里面没有把 value 改成 public，其他普通外部代码也没有因此得到相同权限。
友元关系要由被访问的那个类主动声明，而且不是自动双向的。Score 信任 Auditor，不表示 Score 同时就能访问 Auditor 的私有数据。友元也不会自动传给友元的朋友或派生类。把它理解为有明确授予方向的访问许可，比理解成“两个类从此没有边界”更准确。''',FRIEND_CLASS,'80\n'.replace('\\n','\n'),['许可由 Score 主动授予','Auditor 成员可以访问','不自动双向、传递或继承'],diagram='friend',runner=r'''Score s; Auditor a; cout << a.read(s) << '\n';''')
scene(c,'04-q','课堂练习：只读对象能否修改', '''Score 的 get 是 const 成员函数，set 是普通修改函数。现在对象 s 自己也声明成 const，随后调用 s 点 set，把分数改成九十。它能编译吗？
请先看对象提供的使用条件，再看所调用的函数是否承诺只读。不要因为 set 本来是 public，就认为任何对象状态下都可以调用。
四秒之后，我们分别说明“允许从外部看见这个名字”和“允许在 const 对象上调用”这两层检查。''',r'''const Score s(80);
s.set(90);''','编译失败：不能用 const 对象调用此非 const 成员函数。',notes=['public 不等于总能调用','对象是 const','set 会修改普通成员'],kind='question',context=CONST,verify='compile_error',diagnostic='discards qualifiers')
scene(c,'04-a','答案：const 约束也必须满足', '''这段不能编译。public 说明外部代码有权访问这个接口，而 const 对象只能调用适用于只读对象的成员函数。set 没有 const 承诺，不能拿 s 这样调用。
如果需求只读取，使用 get 就能得到八十。如果确实要修改，就应当从一开始使用可修改对象，再通过受控接口修改，而不是随意去掉 const 约束。
到这里，封装不仅是把字段藏起来，还包括准确表达接口的使用条件。this 说明当前对象是谁，const 说明这次访问能否修改，static 表达类共享数据，friend 则授予特定协作者访问许可。把这几种机制分别放回它解决的问题，就不会只剩下一张关键字表。''',r'''const Score s(80);
cout << s.get() << '\n';''','80\n'.replace('\\n','\n'),['原题违反 const 调用约束','只读对象使用 const 查询接口','访问权限与只读约束要一起检查'],diagram='const',context=CONST)

c=chapter('05','对象组合','Object Composition',5)
MEMBER=r'''class Name {
    string text_;
public:
    Name(string text) : text_(text) {}
    const string& get() const { return text_; }
};
class Student {
    Name name_;
public:
    Student() : name_("Ana") {}
    void show() const { cout << name_.get() << '\n'; }
};'''
scene(c,'05-1','一个对象里面可以有另一个对象', '''成员变量不必只是整数，也可以是我们定义的其他类对象。Student 里面放一个 Name 对象，就把“学生具有姓名”直接写进了组成关系。
创建 Student 时，要先创建它的成员 name。Name 需要一个字符串参数，所以 Student 的初始化列表把 Ana 交给它。等 name 准备好，Student 才继续完成自己的构造过程。
这里表达的是“学生有一个姓名部分”，不是“学生是一种姓名”。前一种关系用组合很自然，后一种才可能涉及继承。先根据含义选择数据关系，不要因为学会继承就把所有代码都改成继承。成员对象有自己的构造要求，包含它的对象需要把这些要求安排好。''',r'''class Student {
    Name name_;
public:
    Student() : name_("Ana") {}
    void show() const { cout << name_.get() << '\n'; }
};''','Ana\n'.replace('\\n','\n'),['Student 包含一个 Name 成员','先构造成员，再执行外层函数体','“有一个”适合考虑组合'],diagram='composition',context=MEMBER.split('class Student')[0],runner=r'''Student s; s.show();''')
PART=r'''class Part {
    char name_;
public:
    Part(char name) : name_(name) { cout << name_ << " "; }
    ~Part() { cout << "~" << name_ << " "; }
};'''
BOX_REVERSE=r'''class Box {
    Part first_;
    Part second_;
public:
    Box() : second_('B'), first_('A') { cout << "Box "; }
};'''
scene(c,'05-2','成员构造顺序看声明顺序', '''有多个成员对象时，先构造谁？关键依据是它们在类里面的声明顺序，不是初始化列表的书写先后。
屏幕先声明 first，再声明 second。即使初始化列表把 second 写在前面，实际仍然先构造 A，再构造 B，最后进入 Box 构造函数体显示 Box。离开作用域时，成员再按相反顺序结束。
这种不一致的写法还会得到编译器的顺序警告。实际写代码时，应当把初始化列表也写成声明的同样顺序，方便阅读。本页故意交换它们，只是为了让你看见规则：声明顺序决定成员对象的实际初始化顺序，不能通过在冒号后面重新排列来改变它。''',BOX_REVERSE,'A B Box ~B ~A \n'.replace('\\n','\n'),['实际顺序由成员声明决定','本例会给出初始化顺序警告','实践中让列表与声明保持一致'],diagram='order',context=PART,runner=r'''{ Box b; } cout << '\n';''',verify='reorder_warning')
BOX=r'''class Box {
    Part first_;
    Part second_;
public:
    Box() : first_('A'), second_('B') { cout << "Box "; }
    ~Box() { cout << "~Box "; }
};'''
scene(c,'05-3','先建内部，结束时反过来', '''把外层 Box 的析构函数也加上，就能看见完整顺序。创建时，先构造成员 A、成员 B，再执行 Box 构造函数体。销毁时，先执行 Box 析构函数体，再销毁成员 B、成员 A。
注意析构函数体开始执行时，成员对象还没有被逐个销毁，所以顺序不是先把成员都清掉，再进入外层析构函数体。
把组合对象想成由内到外准备、再由外到内收尾，就比较容易记住。这里没有涉及动态内存，全部对象都通过正常作用域结束。我们用打印观察先后关系，但真正管理资源时，成员对象自己的收尾动作也会沿着这个结构自动发生。''',BOX,'A B Box ~Box ~B ~A \n'.replace('\\n','\n'),['构造：A、B、Box 函数体','析构：Box 函数体、B、A','顺序来自对象的组成关系'],diagram='order',context=PART,runner=r'''{ Box b; } cout << '\n';''')
scene(c,'05-q','课堂练习：初始化列表能改顺序吗', '''Box 先声明 first，再声明 second，但初始化列表把 second 写在前面。创建时首先显示 A，还是首先显示 B？
请先看类内成员的声明，再看各个成员接收的参数。初始化列表里的参数会交给对应成员，但书写顺序本身能不能改变它们的实际建立次序？
四秒之后，我们把创建和销毁都用正确的顺序列出来，再把初始化列表也整理成容易阅读的版本。''',BOX_REVERSE,'A B Box ~B ~A \n'.replace('\\n','\n'),['先声明 first_','first_ 的参数是 A','区分参数归属与执行顺序'],kind='question',context=PART,runner=r'''{ Box b; } cout << '\n';''',verify='reorder_warning')
scene(c,'05-a','答案：first 仍然先创建', '''先显示 A。因为 first 在类里面先声明，它先被构造；然后才是 second 的 B，再进入 Box 函数体。
修正版把初始化列表也按 first、second 排好，只改善代码的表达，不改变原本的实际构造顺序。这个版本没有专门的 Box 析构输出，所以结束时只看到成员 B 和 A 依次收尾。
这道题以后也能帮助你判断派生对象的构造：不要只看某一行列表怎么排，而要先确定语言对每一种对象部分规定了什么先后。先识别基类和成员，再看传入参数，最后才看构造函数体。''',BOX.replace('    ~Box() { cout << "~Box "; }\n',''),'A B Box ~B ~A \n'.replace('\\n','\n'),['A → B → Box','结束时 B → A','列表按声明顺序写清楚'],diagram='order',context=PART,runner=r'''{ Box b; } cout << '\n';''')
