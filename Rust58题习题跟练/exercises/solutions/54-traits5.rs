// ============================================================================
// 第 54 题 · traits5 —— 多重特征约束：两个能力都要有（impl A + B）
// ----------------------------------------------------------------------------
// 题目类型：compile（把代码改到能编译通过就算过关）
// 课件位置：第 5 章 · 5.3 特征（多重约束 `impl A + B`）
// 难度：★★★☆☆
// 前置知识：第 53 题 traits4（impl Trait 作参数）、布尔运算 &&（primitive_types1）
// ============================================================================
//
// 【题目要求】
// 只允许修改 `fn some_func(item: ??) -> bool` 这一行，让代码编译通过。
// 函数体里同时调用了 `item.some_function()` 和 `item.other_function()`，
// 所以 item 必须**同时**具备两种能力。
//
// 原题代码（未完成，仅供对照）：
//     pub trait SomeTrait { fn some_function(&self) -> bool { true } }
//     pub trait OtherTrait { fn other_function(&self) -> bool { true } }
//
//     fn some_func(item: ??) -> bool {
//         item.some_function() && item.other_function()
//     }
//
// 如果只写一个 trait，比如 `item: impl SomeTrait`，会报：
//     error[E0599]: no method named `other_function` found
//     （因为 impl SomeTrait 只保证 some_function 存在）
//
// 【解题思路】
// 1. 函数体需要两种方法 → 参数必须同时实现两个 trait。
// 2. Rust 用 `+` 把多个约束连起来：
//        fn some_func(item: impl SomeTrait + OtherTrait) -> bool
//    读作：“item 是某个类型，它既实现了 SomeTrait，又实现了 OtherTrait”。
// 3. 两个结构体（SomeStruct、OtherStruct）都已经同时实现了这两个 trait，
//    所以 main 里两次调用都能通过编译。
// 4. `&&` 是逻辑与：左边为 true 才看右边，两个都为 true 结果才是 true。
//    本题两个方法都用默认实现，都返回 true，所以函数返回 true。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 单个约束复习（第 53 题）
//       fn f(x: impl Licensed)               // x 必须实现 Licensed
//   等价于泛型写法：
//       fn f<T: Licensed>(x: T)
//
// ● 多个约束：用 `+` 连接
//       fn f(x: impl A + B)                  // 同时实现 A 和 B
//   等价的泛型写法：
//       fn f<T: A + B>(x: T)
//   `+` 读作“并且”。所以 `impl SomeTrait + OtherTrait` 就是
//   “既有 some_function 的能力，又有 other_function 的能力”。
//   打个比方：招聘要求“会开车 + 会英语”——两样都要，缺一样就不行。
//
// ● 约束多了会怎样？
//   约束越多，能传进来的类型越少（限制越强）。
//   所以只加函数体真正需要的能力即可，别乱堆。
//
// ● 为什么不能只写 `impl SomeTrait`？
//   因为 `impl SomeTrait` 对编译器而言意味着：
//   “我知道这个类型有 SomeTrait 里的方法，其他的一概不知道”。
//   于是 `item.other_function()` 找不到 → error[E0599]。
//   这和“人的记忆被清空，只记得证书上写的技能”是一个道理。
//
// ● 两个 trait 都有默认实现（`-> bool { true }`），
//   两个结构体都用空 impl 认领：
//       impl SomeTrait for SomeStruct {}
//   空 impl 合法，因为方法都有默认实现（同第 52 题 traits3）。
//
// ● `&&` 和 `&` 别搞混
//       &&   逻辑与（两个 bool 都为 true 才是 true），有短路求值
//       &    取引用
//   函数体里 `a() && b()` 是逻辑运算，不是引用。
//
// ● 为什么 main 里可以直接 `some_func(SomeStruct {});`？
//   `SomeStruct {}` 造一个值（单元结构体），按值传给函数；
//   函数返回值 bool 被丢弃 —— 这没问题，表达式语句的值可以忽略。
//   （如果你想看到结果，可以写 `println!("{}", some_func(SomeStruct {}));`）
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

// trait 1：带默认实现的“某种能力”
pub trait SomeTrait {
    fn some_function(&self) -> bool {
        true
    }
}

// trait 2：另一个带默认实现的能力
pub trait OtherTrait {
    fn other_function(&self) -> bool {
        true
    }
}

// 两个空结构体（单元结构体），只用来挂 trait 实现
struct SomeStruct {}
struct OtherStruct {}

// 两个类型都同时实现两个 trait（空 impl，全部用默认实现）
impl SomeTrait for SomeStruct {}
impl OtherTrait for SomeStruct {}
impl SomeTrait for OtherStruct {}
impl OtherTrait for OtherStruct {}

// YOU MAY ONLY CHANGE THE NEXT LINE
// 把 ?? 换成 `impl SomeTrait + OtherTrait`：
//   表示参数 item 的类型必须同时实现这两个 trait
//   （`+` 是“并且”，可以继续叠加更多约束，如 impl A + B + C）
fn some_func(item: impl SomeTrait + OtherTrait) -> bool {
    // 同时调用两个 trait 的方法
    // && 是逻辑与：两边都为 true 时整体为 true
    // 只有当两种能力都具备时，这两行方法调用才能通过编译
    item.some_function() && item.other_function()
    // 最后一行表达式即返回值，类型 bool
}

fn main() {
    // SomeStruct 同时实现了两个 trait，可以传入
    // 返回的 true 被丢弃（表达式语句，加不加分号都可以，这里加了）
    some_func(SomeStruct {});

    // OtherStruct 同样同时实现了两个 trait，也可以传入
    some_func(OtherStruct {});
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）`impl SomeTrait + OtherTrait` 的展开形式是什么？
//        fn some_func<T: SomeTrait + OtherTrait>(item: T) -> bool
//    两者完全等价。`impl Trait` 只是省掉了给类型参数起名字的麻烦。
//    需要写多个约束、或者函数体里要提到这个类型名时，用泛型写法。
//
// 2）为什么必须两个约束，少一个都不行？
//    编译器检查方法调用时只看“约束里声明了什么”。
//    约束里没有 OtherTrait，就不知道 item 有 other_function，
//    即使实际上传进来的类型实现了它，也不允许调用 —— Rust 不做这种“偷看”。
//    这是“按合同办事”：合同（约束）里没写的，一律不许调用。
//
// 3）如果传一个只实现了 SomeTrait 的类型会怎样？
//        struct OnlyOne {}
//        impl SomeTrait for OnlyOne {}
//        some_func(OnlyOne {});
//    → error[E0277]: the trait bound `OnlyOne: OtherTrait` is not satisfied
//    这就是约束在“入口处”把关：不合格的类型根本进不来。
//
// 4）main 里的返回值为什么可以直接丢掉？
//        表达式语句的值若为 ()，加不加分号都行；
//        若不为 ()，加不加分号都能编译（但会有 unused_must_use 之类警告吗？）
//    bool 不是 #[must_use]，所以丢掉不会警告。
//    想观察结果可以打印：println!("{}", some_func(SomeStruct {}));
//
// 5）`+` 的上限是多少？
//    可以一直加：`impl A + B + C + D`。
//    但约束太多通常意味着函数职责过重，可以考虑拆分。
//    另外，用 where 子句可以让签名更清晰（进阶写法）：
//        fn f<T>(x: T) -> bool where T: A + B { ... }
//
// 6）trait 默认实现里的 `true` 有没有坑？
//    本题两个方法都直接返回 true，所以 `&&` 结果一定是 true。
//    如果某个实现者重写了方法返回 false，结果就会变 —— 但本题没人重写。
//
// 7）为什么 `struct SomeStruct {}` 和 `SomeStruct {}` 都带花括号？
//    这是单元结构体（unit-like struct）的定义与实例化写法。
//    它没有字段，花括号里是空的，但语法上不能省（除非定义成 struct SomeStruct;）。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 只写一个 trait：
//        fn some_func(item: impl SomeTrait) -> bool
//    → error[E0599]: no method named `other_function` found for type parameter
//      （约束不足）
//
// 2. 用逗号代替加号：
//        fn some_func(item: impl SomeTrait, OtherTrait)
//    → error: expected one of `!`, `(`, `+`, ...（语法错误）
//      逗号会把 OtherTrait 当成第二个参数的类型名
//
// 3. 用 `&` 连接：
//        impl SomeTrait & OtherTrait
//    → 语法错误（多重约束必须用 +）
//
// 4. 忘了给某个结构体实现某个 trait：
//        删掉 impl OtherTrait for OtherStruct {}
//    → error[E0277]: the trait bound `OtherStruct: OtherTrait` is not satisfied
//      （main 里那次调用失败）
//
// 5. 把 `impl Trait` 写成 `dyn Trait`：
//        fn some_func(item: dyn SomeTrait + OtherTrait)
//    → error[E0277]: the size for values of type `dyn ...` cannot be known
//      （trait 对象必须放在引用/Box 后面，且本题没必要用动态分发）
//
// 6. 在函数体里用 `||` 代替 `&&`：
//    → 能编译，但语义变成“任一为 true 即可”，与题目要求不符。
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. 多重约束用 `+` 连接：`impl A + B`，读作“既要 A 又要 B”；
//   2. 等价泛型写法：`<T: A + B>`；
//   3. 编译器只认约束里声明的能力，约束不足就找不到方法（E0599）；
//   4. 能同时实现多个 trait 是 Rust 的常态，一个类型的能力可以自由组合。
//
// 一句话记忆：**方法用到几个 trait，参数就得 `+` 几个 trait；合同上没写的技能不许调用。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 traits5.rs -o traits5.exe
//   .\traits5.exe
// 【预期输出】
//   （无任何输出；本题只要编译通过、退出码为 0 即算过关）
// ============================================================================
