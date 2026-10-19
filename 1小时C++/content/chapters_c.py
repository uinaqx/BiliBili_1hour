from author import chapter,scene

c=chapter('06','继承','Inheritance',6)
PERSON=r'''class Person {
    string name_;
public:
    Person(string name) : name_(name) {}
    void show() const { cout << name_ << '\n'; }
};'''
STUDENT=r'''class Student : public Person {
    int score_;
public:
    Student(string name, int score)
        : Person(name), score_(score) {}
    int score() const { return score_; }
};'''
scene(c,'06-1','公有继承表达一种类型关系','''现在考虑“学生也是一个人”。Person 保存姓名，Student 在人的基础上增加成绩，这就可以用公有继承表达。冒号后面写 public Person，表示 Student 公有继承 Person。
Student 对象里面包含一个 Person 基类部分，除此之外再有自己的成绩成员。创建学生以后，可以调用从 Person 得到的公开 show 函数，也可以调用 Student 自己的 score 函数。
不要把继承理解成简单复制几行代码。它还建立了类型之间的关系，稍后我们可以把学生交给接受 Person 引用的函数。如果只是“里面有一份资料”，用上一章的组合往往更直接；如果确实是“属于这一种类型”，才进一步考虑公有继承。''',STUDENT,'Ana\n80\n',['Student 是一种 Person','对象包含基类部分与新增成员','公有接口可以继续使用'],diagram='inheritance',context=PERSON,runner=r'''Student s("Ana",80); s.show(); cout << s.score() << '\n';''')
scene(c,'06-2','继承不会开放基类私有成员','''继承后，基类的 private 成员仍然不能在派生类函数里直接访问。姓名虽然存在于学生对象的基类部分，但 Student 不能直接拿 name 下划线这个私有成员来使用。
public、protected、private 三种继承方式，主要改变继承得到的公开成员和受保护成员在派生类中的访问级别。公有继承保持它们原来的级别；保护继承把两者都变为 protected；私有继承把两者都变为 private。基类私有成员不会因此变成可以直接访问。
初学阶段先把公有继承用清楚。还有一个默认规则：class 后面如果省略继承方式，默认是 private；struct 则默认 public。为了让类型关系一眼看明白，本课都明确写出 public。''',r'''class Student : public Person {
public:
    Student() : Person("Ana") {}
    void test() { cout << name_; }
};''','编译失败：name_ 是 Person 的私有成员',['public 继承：公开仍公开、保护仍保护','基类 private 不能被派生类直接访问','class 默认私有继承；建议明确写出'],diagram='access',context=PERSON,runner='Student s; s.test();',verify='compile_error',diagnostic='private')
TRACE=r'''class Person {
public:
    Person() { cout << "Person "; }
    ~Person() { cout << "~Person "; }
};
class Student : public Person {
public:
    Student() { cout << "Student "; }
    ~Student() { cout << "~Student "; }
};'''
scene(c,'06-3','先准备基类，再完成派生类','''派生类构造函数需要先把基类部分准备好。前面 Student 的初始化列表调用 Person，传入姓名，然后准备成绩，最后才进入 Student 构造函数体。
这一页为了观察先后，只保留两个带输出的类。创建时先显示 Person，再显示 Student。离开作用域时先执行 Student 的析构函数体，再结束 Person 基类部分，所以看到相反的次序。
如果还有成员对象，顺序就是先构造直接基类，再按声明顺序构造成员，最后执行派生类自己的构造函数体。这里全部是正常作用域内的对象，没有通过基类指针删除对象。先把这个建立和收尾的顺序理解清楚，就能读懂常见的构造题。''',TRACE,'Person Student ~Student ~Person \n',['先基类，再成员，最后派生类函数体','销毁方向相反','初始化列表负责传入基类参数'],diagram='order',runner=r'''{ Student s; } cout << '\n';''')
scene(c,'06-4','基类引用与独立的基类对象','''有一个 Student 对象时，可以让 Person 引用指向它，因为这里是公开而且没有歧义的继承关系。这个引用让我们通过人的接口使用原来的学生，没有新建另一个学生，也没有把原对象改成 Person。
下一行 Person copy 等于 s，却创建了一个独立的 Person 对象。它只复制基类部分，学生新增的成绩没有进入 copy，这种现象通常叫对象切片。原来的 s 仍然完整存在。
反过来，把普通 Person 自动当成 Student 则不成立，因为普通人未必有成绩等学生部分。读题时先看接收位置是引用、指针，还是一个按值保存的新对象。它们看起来都能接收 s，但代表的对象关系并不相同。''',r'''Student s("Ana",80);
Person& ref = s;
ref.show();
Person copy = s;
copy.show();
cout << s.score() << '\n';''','Ana\nAna\n80\n',['基类引用：使用原来的派生对象','基类值对象：只保留基类部分','派生到基类可以；反向不自动成立'],diagram='slicing',context=PERSON+'\n'+STUDENT)
scene(c,'06-q','课堂练习：基类引用会复制吗','''看这两行初始化。ref 是基类引用，copy 是一个独立的基类对象，它们都从同一个学生 s 得到。哪一个仍然引用原来的学生？哪一个只保存自己的 Person 部分？
这里先不讨论虚函数，只判断有没有创建另一个对象。你可以数一数名字旁边有没有引用符号，再想一想引用在本课开头的含义。
四秒以后，我们分别给这两个位置贴上“使用原对象”和“新建基类对象”的说明。继承的赋值兼容不等于所有对象都可以随意互换，这个区别会直接影响下一章多态的结果。''',r'''Student s("Ana",80);
Person& ref = s;
Person copy = s;
ref.show();
copy.show();''','Ana\nAna\n',['ref 的类型中有 &','copy 是单独的 Person 对象','先判断对象关系，再判断输出'],kind='question',context=PERSON+'\n'+STUDENT)
scene(c,'06-a','答案：引用保留原对象关系','''ref 使用的仍然是 s，所以没有创建独立的 Person 对象。copy 则是新建的 Person，只接收 s 中的基类部分。
两次 show 都显示 Ana，不代表这两种初始化完全一样。因为目前 show 只读取姓名，而这个姓名在两种情况下都存在，所以输出恰好相同。不能只凭一行相同输出就认为两个表达式语义相同。
把这道题和最开始的引用联系起来：引用提供已有对象的另一个使用入口，按值初始化通常建立一个独立对象。继承又让这个独立对象可能只留下基类部分。等我们加入虚函数，保留实际对象的基类引用就有了更明显的用途。''',r'''Student s("Ana",80);
Person& ref = s;   // 使用原对象
Person copy = s;   // 新的基类对象
ref.show();
copy.show();''','Ana\nAna\n',['相同输出不代表相同对象关系','ref → s','copy 只保存 Person 部分'],diagram='slicing',context=PERSON+'\n'+STUDENT)

c=chapter('07','多继承','Multiple Inheritance',3)
MULTI=r'''class Named {
public:
    void name() const { cout << "Ana "; }
};
class Graded {
public:
    int score() const { return 80; }
};
class Student : public Named, public Graded {};'''
scene(c,'07-1','一个派生类可以有多个直接基类','''多继承就是一个类直接继承多个基类。这里 Named 提供姓名显示，Graded 提供成绩读取，Student 同时公有继承两者，所以可以使用这两组公开功能。
先把概念看懂即可，不需要马上在自己的程序里大量使用它。多个基类如果提供同名成员，调用时可能产生歧义，需要明确来自哪一个基类；更复杂的重复继承关系还会增加设计难度。
本课不展开这些复杂结构。你只要认识逗号分隔的基类列表，并且知道每一个基类都有自己的对象部分和构造过程。实际设计时，如果只是把姓名资料和成绩资料装在一起，组合也可能更加清楚；多继承应当服务于明确的类型或接口关系。''',MULTI,'Ana 80\n',['基类列表用逗号分隔','可以获得多组基类接口','本课只掌握基本含义与顺序'],diagram='multiple',runner=r'''Student s; s.name(); cout << s.score() << '\n';''')
ORDER=r'''class A { public: A() { cout << "A "; } };
class B { public: B() { cout << "B "; } };
class C : public A, public B {
public:
    C() : B(), A() { cout << "C\n"; }
};'''
scene(c,'07-2','直接基类按继承列表顺序构造','''多个直接基类先构造谁，看类定义后的基类列表。本页先写 public A，再写 public B，所以先构造 A，再构造 B，最后执行 C 的构造函数体。
即使初始化列表先写 B 再写 A，也不会改变这个顺序。和成员对象一样，编译器会提醒这种书写顺序不一致。正常程序应该把初始化列表也整理成 A、B，让阅读顺序符合实际顺序。
现在把两条规则并排记住：多个直接基类看基类列表顺序，多个成员看类内声明顺序。它们都先于最外层构造函数体。这里讨论的是普通的直接基类，没有引入虚继承；不要把尚未学习的特殊结构混入这道基础顺序题。''',ORDER,'A B C\n',['基类列表：A 在 B 前','实际顺序：A → B → C 函数体','列表书写应与实际顺序一致'],diagram='multiple',runner='C c;',verify='reorder_warning')
scene(c,'07-q','课堂练习：先显示哪一个字母','''C 的基类列表写 A、B，初始化列表写 B、A。创建一个 C，输出是 A B C，还是 B A C？
先找到决定规则的那一处列表，而不是跟着构造函数里最后看见的顺序猜答案。参数可以在初始化列表中指定，但实际执行先后还有语言规定。
请用四秒选出答案，再补一句理由：你依据的是基类列表，还是初始化列表。能说出依据，比只记住这一题的字母顺序更有用。''',ORDER,'A B C\n',['class C : public A, public B','先找决定顺序的列表','不按初始化列表重新排序'],kind='question',runner='C c;',verify='reorder_warning')
scene(c,'07-a','答案：按 A、B 的基类列表执行','''答案是 A B C。A 在基类列表中先出现，先完成 A，再完成 B，最后才进入 C 的构造函数体。
画面已经把初始化列表改成 A、B。输出没有变化，编译器的顺序警告却消失了，因为文字顺序现在符合真实执行顺序。
多继承这一节到这里就够了。以后读到类似代码，先数直接基类，再看基类列表的先后；读到组合对象，则看成员声明的先后。把两种列表的作用分清，就不必靠猜测理解构造输出。''',ORDER.replace('C() : B(), A()','C() : A(), B()'),'A B C\n',['A → B → C','修改列表提高可读性','普通直接基类按继承列表构造'],diagram='multiple',runner='C c;')

c=chapter('08','重载','Overloading',5)
FUN=r'''int twice(int x) { return x * 2; }
double twice(double x) { return x * 2; }'''
scene(c,'08-1','同一个函数名接收不同参数','''函数重载允许多个函数使用同一个名字，只要参数列表能够区分。这里一个 twice 接收整数，一个接收 double。调用 twice 括号三，选择整数版本；传入三点五，选择 double 版本。
编译器在编译时根据参数寻找适合的版本，不是运行以后随意挑选。你可以把重载理解成：同一个动作名字，为几种不同输入分别准备做法。
实际代码还可能涉及类型转换和更复杂的候选比较。初学阶段先让调用清楚：参数类型尽量明确，不要把大量相近类型和默认参数混在一起制造歧义。这里显示六和七，都是乘二的结果，但函数接收到的数据种类不同。''',FUN,'6\n7\n',['函数名相同，参数列表有区别','根据调用参数选择版本','发生在编译阶段'],diagram='overload',runner=r'''cout << twice(3) << '\n'; cout << twice(3.5) << '\n';''')
scene(c,'08-2','只改变返回类型不能重载','''下面两个 read 都没有参数，一个返回 int，一个返回 double。它们不能仅凭返回类型组成重载，因为调用 read 括号时，参数并没有提供任何区别。
不要以为左边变量是 double，编译器就会因此选出返回 double 的 read。对于这种普通函数重载，必须先从参数列表等合法差异区分函数，不能只让返回类型承担区别。
参数个数不同、参数类型不同，都可以形成常见的重载。只有参数名字变了也不算区别，因为名字只是函数内部使用的称呼。本页会在编译阶段失败，没有运行结果；修正办法是改名，或者重新设计参数，使调用本身能清楚表达要做什么。''',r'''int read() { return 1; }
double read() { return 1.5; }''','编译失败：仅返回类型不同，不能重载',['返回类型不能单独区分重载','参数名字不同也不够','调用应当清楚表达意图'],diagram='overload',runner='cout << read();',verify='compile_error',diagnostic='ambiguating')
POINT=r'''struct Point {
    int x;
    int y;
    Point operator+(const Point& other) const {
        return {x + other.x, y + other.y};
    }
};'''
scene(c,'08-3','让加号表达两个点相加','''运算符重载把已有运算符与自定义类型的操作联系起来。Point 保存两个坐标，我们希望两个点相加时，把横坐标相加、纵坐标相加。
operator 加号就是这个操作的函数名。左边的对象通过成员函数的当前对象提供坐标，右边的对象通过 other 引用传进来。函数返回一个新的 Point，不改变原来的两个点。
参数使用 const 引用，表示读取右边对象；成员函数末尾再写 const，表示读取左边对象的普通成员。返回大括号里的两个值，会建立结果点。调用时可以写 a 加 b，但你仍然应该知道它背后执行了一个函数。先理解数据如何进入、结果如何返回，再看简洁写法。''',POINT,'4 6\n',['左边对象提供当前 x、y','other 提供右边坐标','返回新 Point，原对象不变'],diagram='operator',runner=r'''Point a{1,2},b{3,4}; Point c=a+b; cout << c.x << " " << c.y << '\n';''')
scene(c,'08-4','重载沿用原有语法规则','''运算符重载不是创造任意新符号。它不能把加号变成比乘号优先，也不能改变一个运算符需要几个操作数。我们只是在已有语法允许的位置，为自定义类型提供操作。
本页把上一页的调用展开。a 点 operator 加号，传入 b，和 a 加 b 使用同一个成员运算函数。两种形式都会得到四和六。
设计重载时，让含义接近日常直觉非常重要。点加点返回新点容易理解；如果加号暗中修改右边对象，读者就很容易误判。本课只演示加法，不追求一次写全所有运算符。掌握一个清楚的例子，比记一张符号列表更能帮助你阅读真实代码。''',r'''Point a{1,2};
Point b{3,4};
Point c = a.operator+(b);
cout << c.x << " " << c.y << '\n';
cout << a.x << " " << a.y << '\n';''','4 6\n1 2\n',['a + b 调用对应的 operator+','优先级、操作数个数保持原规则','操作含义应当直观'],diagram='operator',context=POINT)
scene(c,'08-q','课堂练习：相加以后原对象变了吗','''a 的坐标是一和二，b 是三和四。执行 c 等于 a 加 b，再分别输出 c 和 a，会出现什么结果？
请回到运算符函数内部，找一找有没有给当前对象的 x 或 y 赋新值。只出现加法表达式和返回新对象，是否等于把左边对象原地改掉？
四秒以后，我们沿着返回值走一次。不要只看加号长什么样，而要根据函数实际执行的动作判断状态。不同程序可以为运算符写不同实现，这一道题的答案来自画面上明确给出的实现。''',r'''Point a{1,2}, b{3,4};
Point c = a + b;
cout << c.x << " " << c.y << '\n';
cout << a.x << " " << a.y << '\n';''','4 6\n1 2\n',['看 operator+ 的实现','返回新对象不等于原地修改','分别跟踪 c 与 a'],kind='question',context=POINT)
scene(c,'08-a','答案：结果放进新的点','''c 是四和六，a 仍然是一和二。这个 operator 加号只读取两个对象，然后返回包含结果的新对象。
如果写 a 等于 a 加 b，情况才不同：先计算新点，再把结果赋给 a。导致 a 改变的是后面的赋值，不是这个加法函数在内部修改了 a。
我们现在就多执行这一行。第二次输出 a 时，它才显示四和六。把计算、返回、赋值分开理解，能避免把所有符号都混成一个动作。函数重载和运算符重载最后都要回到同一个问题：选中了哪个函数，它读了哪些数据，是否修改对象，返回了什么。''',r'''Point a{1,2}, b{3,4};
Point c = a + b;
cout << c.x << " " << c.y << '\n';
cout << a.x << " " << a.y << '\n';
a = a + b;
cout << a.x << " " << a.y << '\n';''','4 6\n1 2\n4 6\n',['c：4、6；原 a：1、2','a = a + b 才把结果保存回 a','计算与赋值是两个步骤'],diagram='operator',context=POINT)
