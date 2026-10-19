from author import chapter,scene

c=chapter('09','多态','Polymorphism',8)
HIDDEN=r'''class Base {
public:
    void show(int n) const { cout << n << '\n'; }
};
class Derived : public Base {
public:
    void show() const { cout << "Derived\n"; }
};'''
scene(c,'09-1','同名隐藏不要求参数相同','''先处理一个容易混淆的问题。Base 有一个接收整数的 show，Derived 又定义一个没有参数的 show。用 Derived 对象直接调用 show 括号七，会编译失败。
原因是派生类里面出现了同名函数，直接从这个派生类名字查找时，基类的同名函数被隐藏了。即使参数不同，也可能发生隐藏，所以它不是我们上一章那种自动合并全部候选的情况。
这还不是虚函数覆盖。基类 show 没有 virtual，而且两个函数参数不同。先把“查找时看不见基类同名函数”和“通过基类接口调用派生实现”分开。前一种叫隐藏；后一种需要虚函数等条件，我们马上逐步建立。''',HIDDEN,'编译失败：Derived 的 show 隐藏了基类同名函数',['同名就可能发生隐藏','参数不同也不自动合并候选','隐藏与虚函数覆盖是不同概念'],diagram='hiding',runner='Derived d; d.show(7);',verify='compile_error',diagnostic='no matching function')
USING=HIDDEN.replace('    void show() const', '    using Base::show;\n    void show() const')
scene(c,'09-2','把基类的同名函数引入作用域','''如果希望 Derived 同时提供这两种 show，可以在它的公开部分写 using Base 双冒号 show。这一行把基类的同名函数引入当前作用域，参与调用选择。
现在 d 点 show 没参数，使用派生类版本；带一个整数七，就能选择基类接收整数的版本。我们没有修改基类函数体，只是明确了派生类范围里允许使用哪些同名函数。
也可以用明确的基类限定来调用指定函数，但这里先掌握 using 这一种常见整理方式。它帮助你理解隐藏和重载之间的关系：先找到可以考虑的名字，再根据参数选函数。它并不自动让函数变成 virtual，也不等于实现了运行时多态。''',USING,'Derived\n7\n',['using Base::show 引入基类函数','show() 与 show(int) 均可调用','这一步仍然不是动态绑定'],diagram='hiding',runner=r'''Derived d; d.show(); d.show(7);''')
NONV=r'''class Base {
public:
    void speak() const { cout << "Base\n"; }
};
class Derived : public Base {
public:
    void speak() const { cout << "Derived\n"; }
};'''
scene(c,'09-3','普通函数看使用入口的类型','''现在让两个类都有完全同样参数的 speak，但暂时不写 virtual。直接用派生类对象 d 调用，显示 Derived。再让一个 Base 引用指向 d，通过这个引用调用，就显示 Base。
这里引用没有复制对象，原对象仍然是 Derived。输出不同，是因为 speak 还只是普通成员函数，通过 Base 类型的入口调用时，选的是 Base 的这个函数。
所以“基类引用指向派生对象”本身还不足以产生我们需要的多态。必须在基类接口中明确说明：这个函数允许根据实际对象选择派生实现。完成这项说明的关键字，就是下一页要加入的 virtual。先看清未使用它时的行为，才容易理解它改变了什么。''',NONV,'Derived\nBase\n',['d.speak()：Derived','Base 引用调用普通函数：Base','原对象类型并没有被引用改变'],diagram='dispatch-static',runner=r'''Derived d; d.speak(); Base& ref=d; ref.speak();''')
VIRTUAL=r'''class Base {
public:
    virtual void speak() const { cout << "Base\n"; }
    virtual ~Base() = default;
};
class Derived : public Base {
public:
    void speak() const override { cout << "Derived\n"; }
};'''
scene(c,'09-4','虚函数按实际对象选择实现','''给基类 speak 加上 virtual，再在派生类匹配的函数后写 override。现在同样通过 Base 引用调用，会显示 Derived。
这就是这里要学习的动态绑定：调用入口是基类引用，实际关联的是派生对象，虚函数调用因此选择派生类提供的覆盖版本。引用仍然使用原对象，没有切出一个新 Base。
override 的作用是让编译器检查我们确实覆盖了基类虚函数，写错参数或末尾的 const 时可以及时发现。基类还写了一个默认的虚析构函数，这是多态基类常见的接口写法，方便以后通过基类指针管理对象时正确收尾。本页不用手动申请或释放内存，重点只看 speak 的调用变化。''',VIRTUAL,'Derived\n',['基类 virtual 允许动态选择','派生类 override 要求编译器检查','Base 引用 → 实际 Derived → Derived::speak'],diagram='dispatch',runner=r'''Derived d; Base& ref=d; ref.speak();''')
BAD=VIRTUAL.replace('void speak() const override','void speak() override')
scene(c,'09-5','覆盖时 const 也必须匹配','''这个版本故意漏掉派生类 speak 末尾的 const，却保留 override。编译器会指出它没有覆盖任何基类虚函数。
基类承诺的是“可以在 const 对象上调用的 speak”，派生类只写一个没有 const 的函数，二者并不匹配。参数列表需要对应，成员函数的这些限定也不能随意省略。
修正很直接：把 const 补回来。不要为了消除错误而直接删掉 override，因为那可能只是把本来希望覆盖的函数悄悄写成另一个函数。初学阶段把 override 当作编译器帮忙核对的标记：既然我认为这是覆盖，就请它检查。错误在编译阶段出现，比运行时才发现选错行为更容易定位。''',BAD,'编译失败：缺少 const，override 检查不通过',['覆盖要匹配参数与成员函数限定','漏掉 const 会改变函数','保留 override，让错误尽早暴露'],diagram='dispatch',runner='Derived d;',verify='compile_error',diagnostic='does not override')
ABSTRACT=r'''class Shape {
public:
    virtual int area() const = 0;
    virtual ~Shape() = default;
};
class Square : public Shape {
    int side_;
public:
    Square(int side) : side_(side) {}
    int area() const override { return side_ * side_; }
};'''
scene(c,'09-6','抽象类规定共同接口','''如果基类只想规定“每一种图形都应能计算面积”，却没有一个适用于所有图形的面积公式，可以把 area 声明为纯虚函数，在声明末尾写等于零。
包含尚未实现的纯虚函数的类是抽象类，不能直接创建 Shape 对象。Square 给出了符合要求的 area 实现，边长乘边长，所以可以创建具体的正方形。
函数可以接收 Shape 引用，调用共同的 area 接口，而实际对象是边长为四的 Square 时，得到十六。先用一句朴素的话理解：基类规定能做什么，具体类给出怎么做。等于零不是面积返回零，也不是在这里执行赋值，它是声明纯虚函数的专门语法。''',ABSTRACT,'16\n',['纯虚函数：virtual ... = 0','抽象类不能直接实例化','具体类实现接口，再创建对象'],diagram='abstract',runner=r'''Square s(4); const Shape& shape=s; cout << shape.area() << '\n';''')
scene(c,'09-q','课堂练习：引用与按值保存的区别','''基类 speak 已经是 virtual，派生类已经正确 override。现在先让 Base 引用指向 d，再创建一个 Base copy 等于 d，分别调用 speak，会显示什么？
这一次不能只记住“有 virtual 就选派生类”。还要检查调用时真正存在的对象。ref 仍然关联 d，但 copy 是不是一个独立的基类对象？
请用四秒把两次调用分开判断。我们在继承一章留下的“引用保留原对象，基类值对象只保存基类部分”，现在正好可以解释答案。''',r'''Derived d;
Base& ref = d;
Base copy = d;
ref.speak();
copy.speak();''','Derived\nBase\n',['先判断 ref 与 copy 关联的实际对象','virtual 根据实际对象选择实现','按值保存可能发生对象切片'],kind='question',context=VIRTUAL)
scene(c,'09-a','答案：引用调用派生版本，副本调用基类版本','''先显示 Derived，再显示 Base。ref 关联的是原来的派生对象，所以虚函数选择 Derived 的覆盖版本。copy 本身就是一个 Base 对象，学生或派生部分没有被保存进去，调用自然选择 Base。
动态绑定不会把一个真实的 Base 对象凭空还原成 Derived。它根据调用当时实际对象的情况选择实现，而不是追溯这个对象最早从谁复制而来。
把多态题分成三步就不容易乱：首先判断基类函数是不是 virtual，然后判断派生类是否正确覆盖，最后判断调用入口背后到底是哪一个对象。引用、指针和按值对象的区别，要放在这最后一步一起看。''',r'''Derived d;
Base& ref = d;
Base copy = d;
ref.speak();   // 原对象是 Derived
copy.speak();  // copy 自己是 Base''','Derived\nBase\n',['检查 virtual','检查 override 是否匹配','检查实际对象，留意切片'],diagram='dispatch-slicing',context=VIRTUAL)

c=chapter('10','异常处理','Exception Handling',6)
DIVIDE=r'''double divide(double a, double b) {
    if (b == 0) {
        throw std::invalid_argument("zero divisor");
    }
    return a / b;
}'''
scene(c,'10-1','无法完成时把问题交给调用者','''最后学习异常处理。计算函数接收到零作为除数时，没有一个正常的除法结果。这里不冒险继续计算，而是用 throw 抛出一个异常对象，说明参数不合适。
抛出以后，当前函数不会继续执行后面的 return。调用者可以在合适的位置接住这个问题，再决定显示提示、重新输入，还是结束当前操作。
这里选择标准库的 invalid argument，意思是传入的参数不符合要求。它需要对应的标准头文件。异常不是正常结果的另一种数字，也不是每一个普通分支都应该使用的手段。先把它理解成：当前步骤不能按约定完成，需要离开正常执行路线，把失败信息交给负责处理的位置。''',DIVIDE,'4\n',['throw 离开正常执行路线','本例先检查零除数','正常输入仍然直接返回结果'],diagram='exception',runner=r'''cout << divide(8,2) << '\n';''')
TRY=r'''try {
    cout << divide(8,0) << '\n';
    cout << "after divide\n";
} catch (const std::exception& e) {
    cout << "caught\n";
}
cout << "continue\n";'''
scene(c,'10-2','try 与 catch 安排处理位置','''把可能抛出异常的调用放进 try。后面的 catch 写明愿意处理哪一类异常，本页用标准异常基类的 const 引用接收，避免为了接收问题再复制或切掉异常对象的一部分。
divide 抛出以后，try 中余下的 after divide 不会执行。程序跳到匹配的 catch，显示 caught。这个 catch 正常结束以后，再执行整组 try catch 后面的 continue。
因此异常并不意味着整台程序一定立刻结束。有没有匹配处理位置、处理完做什么，决定了接下来的路线。如果始终没有合适的处理者，程序可能终止；本例已经提供了处理位置，所以可以清楚观察跳转以后继续的地方。''',TRY,'caught\ncontinue\n',['throw 后跳过 try 中余下语句','匹配 catch 负责处理','处理完成后从整组结构后继续'],diagram='exception',context=DIVIDE)
scene(c,'10-3','正常路线与异常路线分开读','''把除数改为二，divide 正常返回四，try 中下一条语句也会执行，然后跳过 catch，最后显示 continue。
同样的程序结构因为输入不同，可以走两条不同路线。没有异常时，不会为了“检查一下”而执行 catch；已经进入 catch 时，也不会再回到刚才抛出的位置继续算那次除法。
读题可以先在纸上画两条线：正常返回沿着 try 继续向下；抛出异常则寻找匹配 catch。这样就不会把正常输出和错误提示都机械地抄一遍。修复错误通常由处理者重新安排新的操作，而不是自动回到 throw 那一行反复重试。''',TRY.replace('divide(8,0)','divide(8,2)'),'4\nafter divide\ncontinue\n',['正常返回：执行 try 剩余语句','没有异常：跳过 catch','异常处理不会自动重试原调用'],diagram='exception-ok',context=DIVIDE)
CATCH=r'''try {
    throw std::invalid_argument("bad score");
} catch (const std::invalid_argument& e) {
    cout << "argument error\n";
} catch (const std::exception& e) {
    cout << "other standard error\n";
}'''
scene(c,'10-4','先接具体类型，再接共同基类','''一组 try 可以配多个 catch。程序按出现顺序寻找第一个匹配的处理者，不会把每一个 catch 都执行一遍。
invalid argument 属于标准异常体系，既能被自己这个具体类型的引用接收，也能被 exception 基类引用接收。所以应该先写具体类型，再写更一般的基类，给具体问题留下专门处理的机会。
本例首先匹配第一个 catch，显示 argument error，第二个 catch 不再执行。变量 e 在真实程序中还可以用来读取错误说明，本页只输出固定文字，避免不同运行环境的提示内容干扰路线判断。类型关系和书写顺序一起决定谁先接到问题，和前面学过的公有继承又联系起来了。''',CATCH,'argument error\n',['按顺序寻找第一个匹配的 catch','具体类型放在一般类型前','catch 通常使用 const 引用'],diagram='catch')
scene(c,'10-q','课堂练习：抛出后还执行哪几行','''try 中先输出 A，再调用零除数的 divide，接着准备输出 B。catch 输出 C，整组结构之后输出 D。最终会出现哪几个字母？
先从 A 出发，遇到 divide 时检查参数。它是正常返回，还是抛出异常？选定路线以后，再决定 B 有没有机会执行。
四秒以后，我们再补上一个细节：函数里已经创建的自动对象，在异常离开作用域时也会按规则收尾。但先把本题的基本跳转看清，不要因为看见四条输出，就认为四条都一定执行。''',r'''try {
    cout << "A ";
    divide(8,0);
    cout << "B ";
} catch (const std::exception& e) {
    cout << "C ";
}
cout << "D\n";''','A C D\n',['先判断 divide 是否返回','抛出后跳过 B','catch 之后继续到 D'],kind='question',context=DIVIDE)
GUARD=r'''struct Guard {
    ~Guard() { cout << "cleanup "; }
};
void work() {
    Guard g;
    throw std::runtime_error("failed");
}'''
scene(c,'10-a','答案与收尾：跳过余下语句，释放局部对象','''上一题输出 A C D。A 已经执行；零除数触发异常，B 被跳过；匹配 catch 显示 C；处理完成后再显示 D。
本页增加一个带析构函数的局部对象。work 创建 Guard 以后抛出异常，在寻找外层处理者、离开这个函数作用域时，Guard 的析构函数会执行，先显示 cleanup，再由 catch 显示 caught。这种退出途中结束局部对象的过程称为栈展开，先理解现象即可。
这也解释了为什么前面一直强调对象要自己负责收尾：把资源交给合适的对象管理，正常离开和异常离开都能沿着作用域规则处理。本课不展开复杂资源管理，只确认异常路线不是简单跳过所有清理动作。''',GUARD,'cleanup caught\n',['上一题：A → C → D','异常离开作用域时，局部对象析构','本页：cleanup → caught'],diagram='unwind',runner=r'''try { work(); } catch (const std::exception& e) { cout << "caught\n"; }''')

c=chapter('11','综合回顾','Review',2)
scene(c,'11-1','把十个主题连成一张学习地图','''现在把这一小时连起来看。最开始，我们用输入输出和函数完成一个小动作，用引用表达对已有对象的访问。接着把数据和操作放进类，让构造函数建立初始状态，再用访问权限保护对象的使用方式。
组合表达对象内部有哪些部分，继承表达类型之间的关系。它们都有明确的建立和收尾顺序。重载帮助同一个名字接收不同输入，多态则让基类接口根据实际对象选择具体实现。最后，异常处理为无法正常完成的步骤安排另一条路线。
这些词不需要一次背熟。回到每个例子，问四个具体问题：对象在哪里创建？谁能访问它？这次调用选择哪个函数？离开作用域时怎样收尾？能沿着代码回答这四个问题，就已经在真正理解这一课。''',notes=['数据与操作 → 类和对象','初始状态与作用域 → 构造与析构','关系与接口 → 组合、继承、多态','失败路线 → throw、try、catch'],diagram='roadmap')
FINAL=r'''class Score {
    int value_;
public:
    explicit Score(int value) : value_(value) {}
    int get() const { return value_; }
};
void print(const Score& score) {
    cout << score.get() << '\n';
}'''
scene(c,'11-2','用一段小程序开始独立练习','''最后用一段短程序收尾。Score 保存成绩，私有成员不能从外部随意修改。构造函数明确接收初始值，get 允许只读访问，print 通过 const 引用读取已有对象。
构造函数前面还有一个 explicit，这里表示不希望一个普通整数在需要 Score 的位置被悄悄转换成对象。初学时先明确写 Score 括号八十，能够把对象在哪里创建表达得更清楚，不必在这一页展开更多转换规则。
课后请亲手做三步：先把成绩类增加一个经过检查的修改函数；再把两个成绩放进同一个学生对象，练习组合；最后写一个带虚函数的显示接口，练习通过基类引用调用。每改一步就编译一次，对照实际输出解释原因。一小时帮助你建立地图，熟练使用还需要用这些小程序继续练习。''',FINAL,'80\n',['亲手编译，再解释结果','增加修改函数 → 练组合 → 练虚函数','逐步修改，每次只核对一个变化'],diagram='roadmap',runner='Score score(80); print(score);')
