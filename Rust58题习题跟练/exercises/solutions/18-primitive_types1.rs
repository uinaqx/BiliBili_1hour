// ============================================================================
// 第 18 题 · primitive_types1 —— 布尔类型 bool 与 if 条件
// ----------------------------------------------------------------------------
// 题目类型：compile（把代码补全到能编译通过就算过关）
// 课件位置：第 2 章 · 2.2.2 基本类型（布尔类型 bool）
// 难度：★☆☆☆☆
// 前置知识：let 变量（variables1）、if 表达式（if1）、println! 打印（intro2）
// ============================================================================
//
// 【题目要求】
// 按上面 is_morning 的样子，把缺的那一行补完；也可以让它等于 false，
// 只要能编译通过（题目原文：Fill in the rest of the line that has code
// missing!）。
// 原题代码（未完成，仅供对照）：
//     fn main() {
//         // Booleans (`bool`)
//
//         let is_morning = true;
//         if is_morning {
//             println!("Good morning!");
//         }
//
//         let // Finish the rest of this line like the example! Or make it be false!
//         if is_evening {
//             println!("Good evening!");
//         }
//     }
//
// 【解题思路】
// 1. 第二段代码用到了变量 is_evening，但它从来没有被声明 —— 所以编译报错
//    error[E0425]: cannot find value `is_evening` in this scope。
// 2. 照抄第一段的写法：`let is_evening = true;`（或 false）。
// 3. true / false 是 Rust 的两个布尔字面量，类型都叫 bool。
// 4. 选 true，程序会多打印一行 "Good evening!"；选 false 就只打印早上的问候。
//    两种都能编译通过，本题真正的要求只是“补出这个 bool 变量”。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● bool 是什么？
//   bool 是 Rust 的布尔类型，只有两个值：
//     true  —— 真
//     false —— 假
//   它只占 1 个字节，用在条件判断、开关标记这类地方。
//   类型名字和值都是**小写**，写成 True / FALSE 会编译报错（这点和 Python 不同）。
//
// ● 为什么 if 只接受 bool？
//   Rust 明确规定：if 的条件必须是 bool，没有“非 0 即真”的说法。
//     if 1 { }        → error[E0308]: expected `bool`, found integer
//     if "yes" { }    → error[E0308]: expected `bool`, found `&str`
//   这样能避免 C 语言里 `if (x = 5)`（把赋值当条件）那一类经典 bug。
//
// ● let 与不可变性
//     let is_morning = true;
//   声明之后 is_morning 就**不能再改**了。想改要写 `let mut is_morning = true;`。
//   本题不需要改动，所以不用 mut（用了也不会错，只是没必要）。
//
// ● “先声明、必须初始化”
//   Rust 不允许 `let is_evening;` 之后不清不楚地直接用（除非所有分支都给它赋值），
//   所以最简单的写法就是声明时直接给初值。
//
// ● 语句块 { } 与 if
//   if 条件 { ... } 里的 { ... } 是一个“块”，里面可以放多条语句。
//   即使只有一行 println!，大括号也不能省 —— Rust 的 if 大括号是必需的，
//   不像 C 可以写 `if (x) do_something();`。
//
// ● 关于 `fn main()`
//   这是一个可执行程序的入口。编译后运行，会从 main 第一行开始执行。
//   本题是 compile 类型，直接用 rustc 编译即可，不需要 --test。
//
// ● rustlings 的“未完成标记”
//   每道未完成的题里都有一行特殊注释（英文意思是“我还没做完”）。
//   做完题后要把它删掉，rustlings 才认为你完成了。
//
// ● 补充：bool 还能怎么用？
//     - 取反：!is_morning   （true 变 false，false 变 true）
//     - 与：  a && b        （两个都为真才为真）
//     - 或：  a || b        （有一个为真就为真）
//   本模块后面的题（if2、if3）会大量用到这些逻辑运算。
//
// ● 小提示：编译器会告诉你“哪里缺东西”
//   本题报错信息里会明确指出 is_evening 找不到，
//   读错误信息（error[E0425] 后面的英文）是 Rust 学习最重要的技能之一。
//   本答案文件是讲解版，已经去掉了该标记。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

fn main() {
    // ---- 第一部分：布尔变量 is_morning ----
    // true：bool 类型的字面量之一（另一个是 false）
    // 类型可以省略，编译器能直接推断出 is_morning 是 bool
    let is_morning = true;

    // if 的条件必须是 bool；这里 is_morning 自己就是一个 bool，直接写即可
    if is_morning {
        // println! 是“打印并换行”的宏（末尾的 ! 表示宏）
        println!("Good morning!");
    }

    // ---- 第二部分：补上缺失的 is_evening ----
    // 原题这里只写了 let，后面被注释掉了；我们照第一行的样子补完整：
    //   let       声明变量
    //   is_evening 变量名
    //   = false   初值（设为 false，就只打印早上的问候；
    //              想看到 "Good evening!" 可以改成 true）
    //   ;          语句结束
    let is_evening = false;

    // 因为 is_evening 是 false，这个分支不会执行
    if is_evening {
        println!("Good evening!");
    }

    // main 结束；没有返回值，等价于返回 ()（可以理解成别的语言的 void）
}

// ============================================================================
//                            逐 行 解 析
// ============================================================================
//
// let is_morning = true;
//   ├─ let         ：声明变量
//   ├─ is_morning  ：变量名（蛇形命名，全小写，单词用下划线连接）
//   ├─ = true      ：初值是 true
//   └─ ;           ：语句结束
//
// if is_morning { println!("Good morning!"); }
//   ├─ if          ：条件判断
//   ├─ is_morning  ：条件，类型 bool（不需要写 == true）
//   └─ { ... }     ：条件为真时执行的块
//
// let is_evening = false;
//   └─ 与 is_morning 完全同构，只是初值取 false
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 只写 let 不写变量名/初值（原题状态）：
//        let
//    → error: expected pattern, found `if`
//
// 2. 变量名拼错：
//        let is_evenning = false;  if is_evening { ... }
//    → error[E0425]: cannot find value `is_evening` in this scope
//    （Rust 对拼写错误零容忍）
//
// 3. 大小写写错：
//        let is_evening = False;
//    → error[E0425]: cannot find value `False` in this scope
//    （布尔值必须是小写 true / false）
//
// 4. 用 C 的风格写条件：
//        if is_morning == 1
//    → error[E0308]: mismatched types，expected `bool`, found integer
//
// 5. 忘写分号：
//        let is_evening = false
//    → error: expected `;`, found `if`
//
// 6. 字符串字面量用了单引号：
//        println!('Good morning!');
//    → error: character literal may only contain one codepoint
//    （单引号是字符 char，双引号才是字符串 &str；这一点在 primitive_types2 细讲）
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. bool 只有 true / false 两个值，全小写；
//   2. if 的条件必须是 bool，Rust 不做“非 0 即真”的隐式转换；
//   3. 变量声明 `let 名字 = 值;`，不需要时可省略类型；
//   4. 大括号在 Rust 的 if 里不能省略。
//
// 一句话记忆：**条件位置只放 bool，别拿数字当真假。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 primitive_types1.rs -o primitive_types1.exe
//   .\primitive_types1.exe
// 【预期输出】（is_evening 取 false 时）
//   Good morning!
// ============================================================================
