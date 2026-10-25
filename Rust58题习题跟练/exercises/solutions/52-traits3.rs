// ============================================================================
// 第 52 题 · traits3 —— 默认实现：一份代码，两个类型共用
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 5 章 · 5.3 特征（trait 的默认实现 default implementation）
// 难度：★★★☆☆
// 前置知识：第 50、51 题（trait / impl）、结构体（structs1）
// ============================================================================
//
// 【题目要求】
// `Licensed` 这个 trait 要求实现者提供 `licensing_info(&self) -> String`。
// 现在两个结构体（SomeSoftware、OtherSoftware）的授权信息完全一样，
// 题目要求**不要重复写两遍同样的函数**，而是让它们都返回 "Some information"。
//
// 原题代码（未完成，仅供对照）：
//     pub trait Licensed {
//         fn licensing_info(&self) -> String;      // ← 只有签名
//     }
//
//     impl Licensed for SomeSoftware {}            // ← 空 impl，编译不过
//     impl Licensed for OtherSoftware {}           // ← Don't edit this line
//
// 编译器会报：
//     error[E0046]: not all trait items implemented, missing: `licensing_info`
//
// 【解题思路】
// 1. 题目提示“Consider what you can add to the Licensed trait”，
//    意思就是：**trait 里可以给方法写默认实现（函数体）**。
// 2. 把 trait 里那一行从“只有签名”改成“带函数体”：
//        pub trait Licensed {
//            fn licensing_info(&self) -> String {
//                String::from("Some information")
//            }
//        }
// 3. 有了默认实现，实现者就可以什么都不写：
//        impl Licensed for SomeSoftware {}
//    空 impl 也能通过编译，因为它自动继承了 trait 里的默认版本。
// 4. 于是两个结构体共用同一份代码，输出都是 "Some information"，测试通过。
//    注意字符串必须**逐字符完全一致**（大写的 S，中间一个空格）。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 什么是“默认实现”？
//   trait 里的方法可以自带函数体，这个函数体就是“默认行为”：
//       trait Greet {
//           fn hello(&self) -> String {
//               String::from("hello")      // ← 默认实现
//           }
//       }
//   实现者有三种选择：
//       impl Greet for A {}                          // 什么都不写，用默认的
//       impl Greet for B {                           // 自己写，覆盖默认的
//           fn hello(&self) -> String {
//               String::from("hi")
//           }
//       }
//   打个比方：trait 是一份“员工手册模板”，默认实现是模板里已经写好的通用条款；
//   某个部门如果条款不适用，可以自己重写那一节（覆盖）。
//
// ● 默认实现能调用别的 trait 方法吗？
//   能，而且很常用：
//       trait Foo {
//           fn a(&self) -> i32;                 // 必须实现
//           fn b(&self) -> i32 { self.a() * 2 } // 默认实现里调用 a
//       }
//   这样实现者只要写 a，就自动获得 b。
//
// ● 为什么本题 `impl ... {}` 是空的花括号？
//   因为 trait 里所有方法（这里只有一个）都有默认实现，
//   实现者没有必须填的内容，写个空 impl 表示“我认领这份说明书，全部按默认来”。
//   如果 trait 里有任何一个方法没默认实现，空 impl 就会报 E0046。
//
// ● `String::from("Some information")` 和 `"Some information".to_string()` 有区别吗？
//   结果一样，都是创建一个堆上的 String。
//   String::from 是“从 &str 构造 String”的标准写法；
//   to_string 来自 ToString trait（任何能 Display 的类型都能 .to_string()）。
//   本题两种都行，这里用 String::from 与题目测试里的写法保持一致。
//
// ● `&self` 与 `self` 的选择
//   本题 `licensing_info(&self)` 只读取信息、不修改也不消耗对象，
//   所以用不可变借用 `&self` 最合适 —— 调用后对象还能继续用。
//   （对比第 50 题 append_bar 用的是 self，因为它要“改完还给你”。）
//
// ● 关于 `pub`
//   `pub trait Licensed` 表示这个 trait 对外公开。
//   结构体和 impl 没有 pub，所以默认只在当前模块内可见。
//   本题所有代码都在一个文件里，测试通过 `use super::*;` 访问，没问题。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

// 公开的 trait：任何“软件”只要实现它，就拥有授权信息
pub trait Licensed {
    // 注意这里**有函数体**了（原来是分号结尾），这就是默认实现
    fn licensing_info(&self) -> String {
        // 两个类型都返回同样的内容：Some information（注意大小写和空格）
        String::from("Some information")
        // 最后一行表达式即返回值，不需要 return，也不需要分号
    }
}

// 第一个软件：版本号是整数
struct SomeSoftware {
    // 这个字段在本文件里没有被读取过，编译器会给一条 dead_code 警告（不影响通过）
    version_number: i32,
}

// 第二个软件：版本号是字符串
struct OtherSoftware {
    version_number: String,
}

// 空 impl：因为 licensing_info 有默认实现，所以这里什么都不用写
// （题目要求：Don't edit this line —— 这一行保持原样）
impl Licensed for SomeSoftware {}

// 同上，另一个类型也认领这份说明书，同样使用默认实现
impl Licensed for OtherSoftware {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn is_licensing_info_the_same() {
        // 期待的结果：两个类型返回的字符串必须完全一样
        let licensing_info = String::from("Some information");

        // 造两个不同类型的软件实例
        let some_software = SomeSoftware { version_number: 1 };
        let other_software = OtherSoftware {
            version_number: "v2.0.0".to_string(),
        };

        // 因为没有重写方法，两者都走 trait 里的默认实现
        assert_eq!(some_software.licensing_info(), licensing_info);
        assert_eq!(other_software.licensing_info(), licensing_info);
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）为什么“空 impl”是合法的？
//    编译器的规则是：trait 里**没有默认实现**的方法，实现者必须提供。
//    本题唯一的方法有了默认实现，所以“必须提供的方法集合”为空集，
//    空 impl 自然合法。反之，如果删掉函数体（改回分号），
//    空 impl 立刻报 error[E0046]。
//
// 2）默认实现是“复制”还是“共享”？
//    从源码角度看，trait 里只写了一份函数体，两个类型用的是**同一份代码**。
//    编译后，编译器会为每个实现类型生成对应的函数（单态化），
//    但对你写代码而言，只需要维护一份逻辑 —— 这正是题目说的
//    “without writing the same function twice”。
//
// 3）如果以后 OtherSoftware 要返回不同信息怎么办？
//    在它的 impl 里重写这个方法即可：
//        impl Licensed for OtherSoftware {
//            fn licensing_info(&self) -> String {
//                format!("Other v{}", self.version_number)
//            }
//        }
//    这叫作“覆盖（override）默认实现”，和面向对象里的重写很像。
//
// 4）两个结构体里的 version_number 为什么没被用到？
//    本题只考 trait，故意让字段闲置。编译器会警告：
//        warning: field `version_number` is never read
//    这只是警告，不影响编译和测试。真实项目里如果确实要“占位”，
//    可以加 #[allow(dead_code)]，或者干脆把它用起来（比如拼进授权信息）。
//
// 5）`&self` 在这里为什么必须写？
//    因为 trait 规定了 `fn licensing_info(&self)`，impl 里（如果重写）
//    也必须写 `&self`。默认实现同理。如果写成 `self`，
//    调用时 some_software 会被移动，而测试里还要再用它 —— 会报错。
//
// 6）测试里为什么要先存一个 licensing_info 变量？
//    这只是为了可读性：把“期望值”提出来，断言部分更短。
//    也可以直接写 assert_eq!(some_software.licensing_info(), String::from("Some information"))。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 忘了改 trait，直接去写两个 impl（题目禁止重复）：
//    → 能过，但违背题意；而且一旦改文案要改两处。
//
// 2. 默认实现的字符串大小写不一致：
//        String::from("some information")     // 小写 s
//    → 编译通过，但测试 FAILED（字符串比较逐字符）
//
// 3. 忘记返回 String 而是返回 &str：
//        fn licensing_info(&self) -> String { "Some information" }
//    → error[E0308]: mismatched types, expected `String`, found `&str`
//      （&str 不会自动变成 String）
//
// 4. 在 impl 里写了方法但签名不一致：
//        fn licensing_info(self) -> String { ... }
//    → error[E0053]: method `licensing_info` has an incompatible type for trait
//
// 5. 误以为空 impl 不合法，于是给每个类型都复制一份函数：
//    → 能过，但题目明确要求避免重复，属于没读懂考点。
//
// 6. 改动了题目标记 “Don't edit this line” 的那两行：
//    → 例如写成 `impl Licensed for SomeSoftware { }` 其实也一样；
//      但如果写成 `impl Licensed for SomeSoftware;`（少了花括号）会语法错误。
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. trait 方法可以带函数体，这叫默认实现，实现者可以不写直接用；
//   2. 空 `impl Trait for Type {}` 只在“所有方法都有默认实现”时合法；
//   3. 实现者可以重写（覆盖）默认实现，写自己想要的逻辑；
//   4. 只读方法用 `&self`，改值用 `&mut self`，消耗对象用 `self`。
//
// 一句话记忆：**默认实现 = trait 自带的“通用条款”，实现者签名认领即可，想改再覆盖。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test traits3.rs -o traits3.exe
//   .\traits3.exe
// 【预期输出】
//   running 1 test
//   test tests::is_licensing_info_the_same ... ok
//
//   test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
//
// （编译时可能附带 field is never read 的 dead_code 警告，属正常现象。）
// ============================================================================
