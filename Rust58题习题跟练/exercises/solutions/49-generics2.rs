// ============================================================================
// 第 49 题 · generics2 —— 泛型结构体与泛型 impl：让 Wrapper 能装任何类型
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 5 章 · 5.2 泛型（泛型结构体、泛型方法）
// 难度：★★★☆☆
// 前置知识：结构体（structs1、structs2）、impl 方法（structs3）、Vec<T>（第 48 题）
// ============================================================================
//
// 【题目要求】
// 现在的 Wrapper 只能包一个 u32。把它改写成泛型版本，
// 让它能包住**任意类型**（u32、&str ……），两个测试都要通过。
//
// 原题代码（未完成，仅供对照）：
//     struct Wrapper {
//         value: u32,
//     }
//
//     impl Wrapper {
//         pub fn new(value: u32) -> Self {
//             Wrapper { value }
//         }
//     }
//
//     #[test]
//     fn store_str_in_wrapper() {
//         assert_eq!(Wrapper::new("Foo").value, "Foo");   // ← u32 装不下 &str
//     }
//
// 编译器会报：
//     error[E0308]: mismatched types, expected `u32`, found `&str`
//
// 【解题思路】
// 1. 把字段类型 `u32` 换成“待定的类型参数 T”，并在结构体名后声明它：
//        struct Wrapper<T> { value: T }
//    读作“Wrapper 是一个泛型结构体，它有一个字段 value，类型是 T”。
// 2. impl 块也要跟着泛型化：`impl<T> Wrapper<T>`。
//    注意 `impl<T>` 是“声明 T”，`Wrapper<T>` 是“使用 T”，两处都要写，缺一不可。
// 3. `new` 的参数类型从 u32 改成 T，返回值写 `Self`
//    （Self 就是“正在 impl 的这个类型”，这里等于 Wrapper<T>）。
// 4. 函数体 `Wrapper { value }` 不用改：`value` 是字段简写，
//    等价于 `Wrapper { value: value }`。
// 5. 完成之后，`Wrapper::new(42)` 推断出 T = i32，
//    `Wrapper::new("Foo")` 推断出 T = &str，一个结构体服务所有类型。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 结构体复习
//       struct Point { x: i32, y: i32 }     // 定义“形状”
//       let p = Point { x: 1, y: 2 };       // 按形状“造一个值”
//   `struct` 定义的是类型，不是数据；每用一次 `Point { ... }` 才产生一个值。
//
// ● 泛型结构体：字段类型也可以“待定”
//       struct Wrapper<T> { value: T }
//   这就是一份“盒子图纸”：盒子里装什么先不定，用的时候再定：
//       Wrapper<i32>     → value: i32
//       Wrapper<&str>    → value: &str
//       Wrapper<Vec<u8>> → value: Vec<u8>
//   打个比方：`Wrapper<T>` 是奶茶店的空杯（中杯/大杯都行），
//   T 是“你要装什么饮料”。同一个杯型设计，装可乐装奶茶都行。
//
// ● 为什么 struct 和 impl 都要写 <T>？
//       struct Wrapper<T> { value: T }        // ① 声明：Wrapper 需要 1 个类型参数
//       impl<T> Wrapper<T> { ... }            // ② 声明 + 使用
//   ① 处的 `<T>` 是“这个结构体带一个类型参数”。
//   ② 处的 `impl<T>` 是“下面的方法对任意 T 都成立”，
//      后面的 `Wrapper<T>` 才是“给这个具体类型写方法”。
//   如果只写 `impl Wrapper { ... }`，编译器会报：
//       error[E0107]: missing generics for struct `Wrapper`
//       （它不知道 T 该填什么）
//   如果写成 `impl<T> Wrapper { ... }`，同样报 E0107 —— 声明了 T 却没用上，
//   而且 Wrapper 缺参数。所以两处必须成对出现。
//
// ● `Self` 是什么？
//   `Self`（首字母大写）是“当前 impl 目标的别名”。
//   在 `impl<T> Wrapper<T>` 里，Self 就等价于 `Wrapper<T>`。
//   好处：以后把结构体改名，方法签名不用跟着改。
//   注意区分 `self`（小写，指“当前这个值”，类似其他语言的 this）
//   和 `Self`（大写，指“当前这个类型”）。
//
// ● 字段初始化简写
//       Wrapper { value: value }  可以简写成  Wrapper { value }
//   规则：变量名和字段名相同时，可以只写一次。这是 Rust 的语法糖。
//
// ● `pub` 是什么？
//   `pub` 表示“公开”，让别的模块/文件也能调用这个函数。
//   本题的测试在 `mod tests` 里，通过 `use super::*;` 引入父模块内容，
//   即使不加 pub 也能访问（子模块可以看父模块的私有项）。
//   这里保留 pub 是为了体现“这是一个对外提供的构造函数”。
//
// ● 泛型方法一定能推断出 T 吗？
//   本题 `Wrapper::new(42)` 里参数是 42，编译器由实参类型反推 T = i32。
//   如果写成 `Wrapper::new()`（无参数），就推不出来，需要写
//   `Wrapper::<i32>::new()` 这种“涡轮鱼（turbofish）”语法显式指定。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

// 泛型结构体：<T> 声明一个类型参数 T，字段 value 的类型就是 T
struct Wrapper<T> {
    value: T,
}

// 为“任意 T 的 Wrapper<T>”实现方法
// impl<T>   —— 声明类型参数 T
// Wrapper<T> —— 给这个泛型类型写方法（两处 T 必须一致）
impl<T> Wrapper<T> {
    // 关联函数 new：不接收 self，相当于“构造函数”
    // 参数 value 的类型是 T（调用时才确定具体是什么）
    // 返回 Self，也就是 Wrapper<T>
    pub fn new(value: T) -> Self {
        // 字段初始化简写：value 既是变量名也是字段名，所以只写一次
        // 完整写法是 Wrapper { value: value }
        Wrapper { value }
        // 最后这个表达式就是返回值（不写 return，也不写分号）
    }
}

// `#[cfg(test)]`：只有用 rustc --test 编译时才包含这个模块
#[cfg(test)]
mod tests {
    // 把父模块（文件顶层）的所有名字导入，才能用 Wrapper
    use super::*;

    #[test]
    fn store_u32_in_wrapper() {
        // Wrapper::new(42)：由实参 42 推断出 T = i32
        // .value 直接读取字段（字段对同 crate 可见）
        assert_eq!(Wrapper::new(42).value, 42);
    }

    #[test]
    fn store_str_in_wrapper() {
        // Wrapper::new("Foo")：由实参 &str 推断出 T = &str
        // 同一个 Wrapper 类型，这次装的是字符串切片
        assert_eq!(Wrapper::new("Foo").value, "Foo");
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）改写前后到底变了什么？
//    改写前：value: u32       —— 只认一种类型，写死了
//    改写后：value: T         —— 类型待定，用时再填
//    其余代码（new 的函数体、测试）几乎不用动，这就是泛型的价值：
//    **把“变化的部分”参数化，逻辑只写一遍。**
//
// 2）`Wrapper::new(42)` 里的 42 是 i32 还是 u32？
//    没有类型标注时，整数字面量默认是 i32。所以 T = i32，
//    断言 `Wrapper::new(42).value == 42` 两边都是 i32，成立。
//    （如果原来写死 u32，42 会被推断成 u32；现在没有约束了，就是 i32。）
//
// 3）`Wrapper::new("Foo").value` 的类型是什么？
//    "Foo" 是 &'static str，所以 T = &'static str。
//    断言右边 "Foo" 也是 &'static str，两个 &str 用 == 比较的是**内容**是否相同
//    （&str 的 PartialEq 比的是文本，不是地址），所以成立。
//
// 4）一个泛型结构体在内存里是什么样？
//    `Wrapper<i32>` 就是“一个 i32”，`Wrapper<&str>` 就是“一个指针 + 一个长度”。
//    泛型本身不引入任何运行时开销 —— 编译器在编译期为每种具体类型
//    各生成一份代码，这叫“单态化（monomorphization）”。
//    所以 Wrapper<i32> 和 Wrapper<&str> 是两个**不同但同源**的类型，
//    不能互相赋值。
//
// 5）能不能给 T 加限制（trait 约束）？
//    可以，语法是 `impl<T: Display> Wrapper<T>`，
//    意思是“只有当 T 能打印时，才有这些方法”。
//    本题不需要（new 只是搬运数据，不调用 T 的任何方法）。
//    第 50~55 题（traits*、quiz3）会大量用到约束。
//
// 6）如果字段是私有的，测试为什么能访问 `.value`？
//    Rust 的可见性规则：字段默认“模块内可见”。
//    测试模块是当前文件的子模块，子模块可以访问祖先模块的私有项，
//    所以 `.value` 能读。若测试在别的文件/别的 crate，就需要 `pub value: T`。
//
// 7）为什么 new 返回 Self 而不是 Wrapper<T>？
//    两者完全等价。用 Self 更短，且改结构体名时不用改这里。
//    注意 Self 只能在 impl 块里用，写在 impl 外面会报错。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. struct 加了 <T>，impl 忘了加：
//        impl Wrapper<T> { ... }
//    → error[E0107]: missing generics for struct `Wrapper`
//      或者 error[E0412]: cannot find type `T` in this scope
//
// 2. impl 加了 <T>，但后面写成 `impl<T> Wrapper { ... }`：
//    → error[E0107]: missing generics for struct `Wrapper`
//      （声明了 T，但 Wrapper 后面没带上它）
//
// 3. 只改 struct 不改 new 的参数类型：
//        struct Wrapper<T> { value: T }
//        pub fn new(value: u32) -> Self { Wrapper { value } }
//    → error[E0308]: mismatched types, expected `T`, found `u32`
//
// 4. 把 T 写在 impl 后面但没声明：
//        impl Wrapper<T> { ... }
//    → error[E0412]: cannot find type `T` in this scope
//      （`impl<T>` 里的 <T> 才是声明）
//
// 5. 以为泛型是“运行时任意类型”（像 Python 那样）：
//    Rust 的泛型在编译期就确定，`Wrapper<i32>` 和 `Wrapper<&str>` 是不同类型，
//    不能放进同一个 `Vec<Wrapper<i32>>`。需要异构容器时用枚举。
//
// 6. 忘记字段简写的规则：
//        Wrapper { value: T }   ← 这会把 T 当成一个值，报错
//    → error[E0423]: expected value, found type parameter `T`
//      （字段简写只对同名变量有效）
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. 泛型结构体写法：`struct 名字<T> { 字段: T }`；
//   2. 泛型 impl 写法：`impl<T> 名字<T> { ... }`，两处 <T> 缺一不可；
//   3. `Self` = 当前 impl 的类型，`self` = 当前的值，大小写意义完全不同；
//   4. 字段初始化简写 `Foo { value }` 等价于 `Foo { value: value }`；
//   5. 泛型不带来运行时开销，编译器会为每种具体类型生成专用代码。
//
// 一句话记忆：**struct 里声明 T，impl 里再声明一次 T，然后两处都把它用在类型名上。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test generics2.rs -o generics2.exe
//   .\generics2.exe
// 【预期输出】
//   running 2 tests
//   test tests::store_str_in_wrapper ... ok
//   test tests::store_u32_in_wrapper ... ok
//
//   test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
// ============================================================================
