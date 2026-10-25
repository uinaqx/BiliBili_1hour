// ============================================================================
// 第 19 题 · primitive_types2 —— 字符类型 char（单引号）与字符方法
// ----------------------------------------------------------------------------
// 题目类型：compile（把代码补全到能编译通过就算过关）
// 课件位置：第 2 章 · 2.2.2 基本类型（字符类型 char，Unicode）
// 难度：★☆☆☆☆
// 前置知识：let 变量、if / else if / else（if1~if3）、bool（第 18 题）
// ============================================================================
//
// 【题目要求】
// 仿照 my_first_initial 那一段，把缺失的那一行补完（自己挑一个喜欢的字符）。
// 原题代码（未完成，仅供对照）：
//     fn main() {
//         // Characters (`char`)
//
//         // Note the _single_ quotes, these are different from the double quotes
//         // you've been seeing around.
//         let my_first_initial = 'C';
//         if my_first_initial.is_alphabetic() {
//             println!("Alphabetical!");
//         } else if my_first_initial.is_numeric() {
//             println!("Numerical!");
//         } else {
//             println!("Neither alphabetic nor numeric!");
//         }
//
//         let // Finish this line like the example! What's your favorite character?
//         // Try a letter, try a number, try a special character, try a character
//         // from a different language than your own, try an emoji!
//         if your_character.is_alphabetic() {
//             println!("Alphabetical!");
//         } else if your_character.is_numeric() {
//             println!("Numerical!");
//         } else {
//             println!("Neither alphabetic nor numeric!");
//         }
//     }
//
// 【解题思路】
// 1. 第二段用到了 your_character，但它没有被声明过：
//    error[E0425]: cannot find value `your_character` in this scope
// 2. 照第一段的样子补一行：`let your_character = 'A';`
//    注意用**单引号** 'A'，不能用双引号 "A"。
// 3. 'A' 是字母，所以 is_alphabetic() 返回 true，程序打印 "Alphabetical!"。
// 4. 想玩点别的：'7' 会走数值分支；'#' 两个都不是；'李' 在 Unicode 里也算
//    字母（Alphabetic），也是 "Alphabetical!"。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● char 是什么？
//   char 表示**一个** Unicode 字符，用单引号包起来：
//     let c = 'A';      // 字母
//     let d = '7';      // 数字字符（不是数字 7）
//     let e = '#';      // 符号
//     let f = '李';     // 中文
//     let g = '🦀';     // emoji（也是一个 char）
//   Rust 的 char 是 4 个字节（32 位），所以能装下任何 Unicode 标量值，
//   不像 C 的 char 只有 1 字节、只能装 ASCII。
//
// ● 单引号 'A' 和双引号 "A" 完全不同
//     'A'  → char，一个字符
//     "A"  → &str，一段字符串（长度可以是 1，也可以是 0 或很多）
//   这是初学者最容易混的地方：**单引号是字符，双引号是字符串。**
//   （注意：'A' 合法，但 'AB' 不合法 —— char 只能装一个字符。）
//
// ● 字符串字面量给 println! 时也是 &str
//   println!("Alphabetical!"); 这里的 "Alphabetical!" 是 &str，
//   与 char 没有关系；printf 风格的 {} 可以打印 char，也可以打印 &str。
//
// ● char 上的常用方法（在标准库里定义）
//     c.is_alphabetic()  → 是字母吗？（bool）
//     c.is_numeric()     → 是数字吗？（bool）
//     c.is_whitespace()  → 是空白吗？
//     c.to_ascii_uppercase() → 变大写
//   调用方法用“点号”：变量名.方法名(参数)。
//   这里的 is_alphabetic 是 Unicode 意义上的字母，所以 '李' 也返回 true。
//
// ● else if 链（复习 if2、if3）
//   三个分支依次判断：先问“是字母吗”，再问“是数字吗”，都不是走 else。
//   每个分支里只有 println! 语句（返回 ()），所以这个 if 表达式整体类型是 ()，
//   不需要赋值给任何变量 —— 它只是“执行一段逻辑”。
//
// ● 字符字面量里怎么表示特殊字符？
//     '\n'    换行        '\t'    制表符
//     '\\'    反斜杠      '\''    单引号本身
//     '\u{1F980}'          用 Unicode 码点表示（这里是一只螃蟹）
//   这些都叫“转义序列”。
//
// ● 编译方式
//   本题有 main，是 compile 类型，直接 rustc 编译运行即可，不需要 --test。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

fn main() {
    // ---------- 第一部分：原题给的例子 ----------
    // 单引号表示 char（一个字符）；这里是大写字母 C
    let my_first_initial = 'C';

    // 是字母吗？'C' 是 → 打印 Alphabetical!
    if my_first_initial.is_alphabetic() {
        println!("Alphabetical!");
    } else if my_first_initial.is_numeric() {
        // 是数字吗？'C' 不是，不会走到这里
        println!("Numerical!");
    } else {
        // 既不是字母也不是数字
        println!("Neither alphabetic nor numeric!");
    }

    // ---------- 第二部分：补上缺失的 your_character ----------
    // 照第一段的写法补完整这一行：
    //   let           声明变量
    //   your_character 变量名（原题后面就是用它来调用方法的）
    //   = 'A'         初值：单个字符，必须用单引号
    //   ;             语句结束
    // 想换个字符试试？把 'A' 换成 '7'、'#'、'李'、'🦀' 都可以，都是合法 char。
    let your_character = 'A';

    // 判断这个字符属于哪一类
    if your_character.is_alphabetic() {
        // 'A' 是字母 → 打印这一行
        println!("Alphabetical!");
    } else if your_character.is_numeric() {
        // 若把 'A' 换成 '7'，就会打印这一行
        println!("Numerical!");
    } else {
        // 若换成 '#'，就会打印这一行
        println!("Neither alphabetic nor numeric!");
    }
}

// ============================================================================
//                            逐 行 解 析
// ============================================================================
//
// let my_first_initial = 'C';
//   ├─ let               ：声明变量
//   ├─ my_first_initial   ：变量名
//   ├─ = 'C'             ：char 字面量（单引号，只能一个字符）
//   └─ ;                 ：语句结束
//
// if my_first_initial.is_alphabetic()
//   ├─ my_first_initial   ：char 类型的值
//   ├─ .                  ：调用方法
//   ├─ is_alphabetic()    ：标准库方法，返回 bool
//   └─ ()                 ：没有参数
//
// let your_character = 'A';   ← 本题唯一需要补的一行
//   └─ 与上面完全同构，只是变量名和字符换了
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 用了双引号：
//        let your_character = "A";
//    → 编译通过，但类型是 &str，后面 your_character.is_alphabetic() 会报错：
//      error[E0599]: no method named `is_alphabetic` found for reference `&str`
//      （&str 的“是不是字母”要用 chars() 逐个字符判断，不能直接调用）
//
// 2. 单引号里放了多个字符：
//        let your_character = 'AB';
//    → error: character literal may only contain one codepoint
//
// 3. 单引号里什么都不放：
//        let your_character = '';
//    → error: empty character literal
//
// 4. 变量名拼错：
//        let your_char = 'A';  if your_character...
//    → error[E0425]: cannot find value `your_character` in this scope
//
// 5. 方法名拼错：
//        your_character.is_alpha()
//    → error[E0599]: no method named `is_alpha` found for type `char`
//
// 6. 忘了调用方法（少了括号）：
//        if your_character.is_alphabetic {
//    → error[E0615]: attempted to take value of method `is_alphabetic`
//
// 7. 把中文当成“非字母”来预期：
//    '李' 的 is_alphabetic() 其实是 true，因为 Unicode 把汉字归为字母类。
//    如果想让程序打印第三种情况，用 '#'、'@' 这种符号更合适。
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. char 是“一个 Unicode 字符”，用单引号，占 4 字节；
//   2. 单引号 = char，双引号 = &str，绝不能混；
//   3. 常用方法：is_alphabetic()、is_numeric()，都返回 bool；
//   4. else if 链可以把“分类判断”写得很清楚。
//
// 一句话记忆：**单引号装一个字符，双引号装一段文本。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 primitive_types2.rs -o primitive_types2.exe
//   .\primitive_types2.exe
// 【预期输出】（your_character 取 'A' 时）
//   Alphabetical!
//   Alphabetical!
// ============================================================================
