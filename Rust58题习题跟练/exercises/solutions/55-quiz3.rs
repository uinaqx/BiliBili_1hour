// ============================================================================
// 第 55 题 · quiz3 —— 综合小测：泛型 + 特征约束 + Display
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 5 章 · 5.2 泛型 + 5.3 特征（综合复习）
// 难度：★★★★☆
// 前置知识：第 48~54 题（generics1~2、traits1~5），尤其第 49、53 题
// ============================================================================
//
// 【题目要求】
// 学校的成绩单系统现在只支持“数字成绩”（2.1、5.5 ……），
// 但学校还会发字母成绩（A+ ~ F-）。要求：
//   1. 改造 ReportCard 结构体和它的 impl，让成绩字段能装**任意能打印的类型**；
//   2. 把第二个测试里的 grade 改成 "A+"，验证字母成绩也能生成成绩单；
//   3. 两个测试都要通过（输出格式一个字符都不能变）。
//
// 原题代码（未完成，仅供对照）：
//     pub struct ReportCard {
//         pub grade: f32,             // ← 写死成 f32，装不了 "A+"
//         pub student_name: String,
//         pub student_age: u8,
//     }
//
//     impl ReportCard {
//         pub fn print(&self) -> String {
//             format!("{} ({}) - achieved a grade of {}",
//                 &self.student_name, &self.student_age, &self.grade)
//         }
//     }
//
//     // 第二个测试里：
//     //     grade: 2.1,   ← 要改成 "A+"
//
// 【解题思路】
// 1. 成绩字段要从“只能装 f32”变成“能装 f32、String、&str ……”，
//    自然想到泛型：`pub grade: T`，并在结构体上声明 `<T>`。
// 2. 但 print 里用 `{}` 打印 grade，`{}` 要求类型实现 `Display` trait。
//    所以在 impl 上加约束：`impl<T: Display> ReportCard<T>`。
//    含义：“只有当 T 能打印时，才有 print 这个方法”。
// 3. 别忘了 `use std::fmt::Display;`（Display 不在预导入列表里）。
// 4. 结构体定义本身**不需要**加约束（存数据不要求能打印），
//    只在 impl 上加即可 —— 这样 ReportCard<某个不能打印的类型> 依然可以被创建，
//    只是不能调用 print。
// 5. 第二个测试把 `grade: 2.1` 改成 `grade: "A+"`，T 变成 &str，
//    &str 实现了 Display，打印出来就是 A+。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 本题是全章综合，先把三块知识串起来
//   (1) 泛型（5.2）：`struct ReportCard<T> { grade: T }` —— 类型待定；
//   (2) 特征（5.3）：`T: Display` —— 待定类型必须“会打印”；
//   (3) 方法（5.1）：`impl<T: Display> ReportCard<T> { fn print(&self) ... }`。
//   一句话：**泛型负责“什么都能装”，约束负责“装的东西得有我要的能力”。**
//
// ● Display 是什么？
//   标准库里的一个 trait，意思是“可以用 {} 显示给用户看”。
//   你平时写的 `println!("{}", x)`，就是要求 x: Display。
//   常见类型的 Display 效果：
//       i32      → 42
//       f32      → 2.1（注意：2.10 会打印成 2.1）
//       &str     → 原样输出
//       String   → 原样输出
//   对比 Debug：`{:?}` 使用的 trait，主要给开发者看（字符串会带引号）。
//
// ● 为什么要把 `T: Display` 写在 impl 上，而不是 struct 上？
//   写在 struct 上：
//       struct ReportCard<T: Display> { grade: T, ... }
//   意味着“创建 ReportCard 时，T 就必须能打印”。
//   写在 impl 上：
//       impl<T: Display> ReportCard<T> { fn print ... }
//   意味着“类型随便存，但只有能打印的 T 才能调用 print”。
//   后者更灵活：约束应该加在**真正需要它的地方**。
//   本题两种写法都能过测试，但推荐后者（题目提示也是这个思路）。
//
// ● `format!` 是什么？
//   和 println! 几乎一样，但它**不打印**，而是把格式化结果作为 String 返回：
//       let s = format!("{} ({})", name, age);
//   本题 print 返回 String，所以必须用 format! 而不是 println!。
//
// ● `&self.grade` 里的 & 有必要吗？
//   没有也行（format! 会自动借用参数）。原题写了 &，我们保持不变。
//   注意 `&T` 也实现 Display（标准库有 `impl Display for &T where T: Display`），
//   所以 `&self.grade` 依然能配 `{}`。
//
// ● u8 是什么？
//   8 位无符号整数，范围 0..=255。用来存年龄正好（12、11）。
//
// ● 为什么姓名是 String 而成绩是泛型？
//   姓名永远是文本，类型固定；成绩可能是数字也可能是字母，类型不固定。
//   泛型只应该用在“真的会变”的地方，别把整个结构体都泛型化。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

// 引入 Display trait：约束 T: Display 需要它，且它不在预导入（prelude）里
use std::fmt::Display;

// 泛型结构体：<T> 声明类型参数 T
// 注意：这里没有给 T 加约束 —— 存数据本身不需要“能打印”
pub struct ReportCard<T> {
    // 成绩：类型是 T（可以是 f32、String、&str ……）
    pub grade: T,
    // 学生姓名：固定是 String
    pub student_name: String,
    // 学生年龄：固定是 u8
    pub student_age: u8,
}

// 为“任意 T，只要 T 实现了 Display”的 ReportCard<T> 实现方法
// 约束写在 impl 上，而不是 struct 上
impl<T: Display> ReportCard<T> {
    // &self：只读借用，打印不应该消耗成绩单
    // -> String：返回拼好的文本
    pub fn print(&self) -> String {
        // format! 把格式化结果作为 String 返回（不打印）
        // {} 依次填入：student_name、student_age、grade
        //   三个占位符都要求对应参数实现 Display
        format!(
            "{} ({}) - achieved a grade of {}",
            &self.student_name, &self.student_age, &self.grade
        )
        // 最后一行表达式即返回值（String）
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn generate_numeric_report_card() {
        // 数字成绩：T 被推断为 f32（字面量 2.1 默认是 f64？）
        // 注意：因为字段没有别的约束，2.1 会按“默认浮点类型 f64”推断，
        // 但 Display 对 f32/f64 都成立，打印结果都是 "2.1"，测试照样通过。
        let report_card = ReportCard {
            grade: 2.1,
            student_name: "Tom Wriggle".to_string(),
            student_age: 12,
        };
        assert_eq!(
            report_card.print(),
            "Tom Wriggle (12) - achieved a grade of 2.1"
        );
    }

    #[test]
    fn generate_alphabetic_report_card() {
        // 字母成绩：把原来的 2.1 改成 "A+"
        // 于是 T 被推断为 &str（字符串字面量的类型），&str 实现了 Display
        let report_card = ReportCard {
            grade: "A+",
            student_name: "Gary Plotter".to_string(),
            student_age: 11,
        };
        assert_eq!(
            report_card.print(),
            "Gary Plotter (11) - achieved a grade of A+"
        );
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）改动清单（一共三处）
//    ① 结构体：`pub struct ReportCard` → `pub struct ReportCard<T>`，
//       字段 `pub grade: f32` → `pub grade: T`；
//    ② impl：`impl ReportCard` → `impl<T: Display> ReportCard<T>`；
//       并在文件顶部 `use std::fmt::Display;`；
//    ③ 第二个测试：`grade: 2.1` → `grade: "A+"`。
//    print 的函数体一个字都不用改。
//
// 2）为什么 print 的方法体不用改？
//    因为 format! 只要求“能 Display”，这和具体是什么类型无关。
//    T: Display 保证了这一点，所以 `{}` 一定能工作。
//    这就是泛型 + 约束的威力：逻辑写一遍，适配所有类型。
//
// 3）数字测试里 T 到底是 f32 还是 f64？
//    原题字段写死 f32，所以 2.1 被当作 f32。
//    改成泛型后，2.1 没有其他约束，Rust 的默认浮点类型是 f64。
//    但两种类型 Display 的结果都是 "2.1"，断言字符串完全一样，测试仍然通过。
//    这正是“约束只要求能力，不要求身份”的体现。
//    （如果你希望保持 f32，可以写 `grade: 2.1f32`，但没必要。）
//
// 4）`&str` 和 `String` 都能配 `{}` 吗？
//    都能：
//        &str   → 原样输出文本
//        String → 原样输出文本
//    所以 `grade: "A+"`（&str）和 `grade: "A+".to_string()`（String）都能过测试。
//    这里用 &str，因为它更短，而且字面量是 'static 的，不存在悬垂问题。
//
// 5）如果把约束写成 `T: Debug` 会怎样？
//    Debug 对应 `{:?}`，而格式串里用的是 `{}`（Display），
//    编译会报：
//        error[E0277]: `T` doesn't implement `std::fmt::Display`
//    记住配对关系：`{}` ↔ Display，`{:?}` ↔ Debug。
//
// 6）能不能不给 T 加约束，改用 `T: ToString`？
//    ToString 也可以（有 `impl<T: Display> ToString for T`），
//    但那样你得写 `self.grade.to_string()` 再拼字符串，
//    不如直接用 Display + format! 自然。题目提示也是 Display。
//
// 7）如果结构体上也加了约束会怎样？
//        pub struct ReportCard<T: Display> { ... }
//    测试照样能过。区别在于：这种写法下，你无法创建
//    `ReportCard<不能打印的类型>`，哪怕你根本不打算调用 print。
//    约束越靠外，限制越强。这是设计取舍，不是语法错误。
//
// 8）测验：这个 print 能不能改成返回 &str？
//    不能。format! 每次都会新建一个 String，它是局部值，
//    返回 &str 会变成“悬垂引用”（指向已释放的内存），编译器会拦住（第 56~58 题讲生命周期）。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 忘了 `use std::fmt::Display;`：
//        impl<T: Display> ReportCard<T>
//    → error[E0405]: cannot find trait `Display` in this scope
//      （可以写全路径 `impl<T: std::fmt::Display>` 绕过，但推荐 use）
//
// 2. 只改 struct 没改 impl：
//    → error[E0107]: missing generics for struct `ReportCard`
//      或 error[E0412]: cannot find type `T` in this scope
//
// 3. impl 写成 `impl ReportCard<T>`（漏了 `<T>` 声明）：
//    → error[E0412]: cannot find type `T` in this scope
//
// 4. 约束写成 `T: Display` 但格式串用了 `{:?}`：
//    → error[E0277]: `T` doesn't implement `Debug`
//
// 5. 第二个测试忘了改成绩：
//        grade: 2.1,
//    → 编译通过，但测试 FAILED：
//      left: "Gary Plotter (11) - achieved a grade of 2.1"
//      right:"Gary Plotter (11) - achieved a grade of A+"
//
// 6. 把 grade 改成字符串但忘了它是 &str：
//        grade: String::from("A+")   ← 也行
//        grade: 'A'                   ← 不行，char 打印出来是 A 而不是 A+
//
// 7. 把 print 的返回类型改成 ()：
//    → error[E0308]: mismatched types, expected `String`, found `()`
//      （format! 的结果被丢弃了）
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. 泛型结构体：`struct 名字<T> { 字段: T }`，用时再填具体类型；
//   2. 特征约束：`impl<T: Display> 名字<T>`，限制“只有能打印的 T 才有这个方法”；
//   3. `{}` 要求 Display，`{:?}` 要求 Debug，两者不能混用；
//   4. `format!` 返回 String（不打印），`println!` 打印（返回 ()）；
//   5. 约束加在“真正需要它的地方”（impl），比加在 struct 上更灵活。
//
// 一句话记忆：**泛型让类型可变，约束保证能力够用；`{}` 要 Display，`format!` 产出 String。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test quiz3.rs -o quiz3.exe
//   .\quiz3.exe
// 【预期输出】
//   running 2 tests
//   test tests::generate_alphabetic_report_card ... ok
//   test tests::generate_numeric_report_card ... ok
//
//   test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
// ============================================================================
