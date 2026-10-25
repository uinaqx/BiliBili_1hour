// ============================================================================
// 第 34 题 · structs3 —— 给结构体装上"方法"：impl、&self、关联函数
// ----------------------------------------------------------------------------
// 题目类型：test（让 4 个 #[test] 测试都通过就算过关）
// 课件位置：第 5 章 · 5.1 方法（impl、&self、关联函数 new）；另含 3.3 结构体
// 难度：★★★★☆
// 前置知识：structs1、structs2（结构体定义/实例化/字段访问）、借用 &self
// 扩展提示：本题含 `#[should_panic]` 测试属性，课件未讲，文中有专门说明
// ============================================================================
//
// 【题目要求】
// Package 表示一个快递包裹，已有结构体定义和关联函数 Package::new(...)
// （重量 <= 0 时 panic）。需要你补全两个方法：
//   - is_international(&self) -> bool：发件国和收件国不同就是国际件；
//   - get_fees(&self, cents_per_gram: i32) -> i32：运费 = 克数 × 每克单价。
// 让 4 个测试全部通过。
//
// 原题代码（未完成，仅供对照）：
//     impl Package {
//         fn new(sender_country: String, recipient_country: String,
//                weight_in_grams: i32) -> Package { ... }   // 已给出
//
//         fn is_international(&self) -> （待填返回类型） {
//             // Something goes here...
//         }
//
//         fn get_fees(&self, cents_per_gram: i32) -> （待填返回类型） {
//             // Something goes here...
//         }
//     }
//
// 测试里会这样调用：
//     Package::new(...)              // 关联函数：用 类型名::函数名 调用
//     package.is_international()     // 方法：用 实例.方法名() 调用
//
// 【解题思路】
// 1. is_international 只需要"读"两个字段做比较，所以接收者是 &self，返回 bool：
//        self.sender_country != self.recipient_country
//    两个 String 内容不相等 → true（国际件）；相等 → false（国内件）。
// 2. get_fees 需要"读"重量，再加一个参数，返回整数运费（i32）：
//        self.weight_in_grams * cents_per_gram
//    重量 1500 克 × 3 分/克 = 4500 分；× 6 = 9000 分，正好对上测试。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 什么是"方法"（method）？
//   方法是"绑定在某个类型上的函数"，和普通函数只差两点：
//     1. 写在 `impl 类型名 { ... }` 块里；
//     2. 第一个参数是 self（或 &self / &mut self），代表"调用它的那个实例"。
//   impl = implementation（实现），一个类型可以有多个 impl 块，效果一样。
//
// ● self、&self、&mut self 三兄弟
//     fn consume(self)          —— 拿走所有权（调用后实例不能再用）
//     fn read(&self)            —— 只读借用（最常用，本题两个方法都用它）
//     fn change(&mut self)      —— 可变借用（要改字段时用）
//   打个比方：self = 把书买回家；&self = 借来看，看完还；
//   &mut self = 借来在上面做笔记，看完还。
//   self 是关键字，不是变量名，写法固定，不需要写类型标注。
//
// ● 关联函数（associated function）与 :: 语法
//   不带 self 参数的函数属于类型、但不属于某个实例，叫"关联函数"。
//   调用方式是 `Package::new(...)`（类型名 :: 函数名），
//   而不是 `package.new(...)`（实例 . 方法名）。
//   new 是社区约定俗成的"构造函数"名字（Rust 没有专门的构造函数语法）。
//
// ● 字段初始化简写（原题 new 里就用了）
//       Package { sender_country, recipient_country, weight_in_grams }
//   当变量名和字段名完全相同时，可以只写一遍（等价于 `字段: 同名变量`）。
//   这也顺便完成了所有权移动：三个参数被搬进结构体字段。
//
// ● panic! 与 assert!/assert_eq!
//   panic!("...")        —— "遇到无法继续的错误，立刻中止"（宏，必须带 !）
//   assert!(条件)        —— 条件为 true 才通过，否则 panic
//   assert!(!条件)       —— 取反：条件为 false 才通过
//   assert_eq!(左, 右)   —— 左右相等才通过，否则打印两边的值
//
// ● #[should_panic]（课件未讲，扩展）
//   普通测试要求"函数正常跑完"；有些测试偏偏要验证"这里应该 panic"。
//   给测试加上 #[should_panic] 后语义反转：
//       测试函数 panic 了   → 测试通过；
//       测试函数正常跑完了 → 测试失败（FAILED）。
//   本题的 fail_creating_weightless_package 就用它验证"负重量必须 panic"。
//   更严格的写法：`#[should_panic(expected = "Can not ship")]`，
//   还要求 panic 信息里包含指定文字。
//
// ● 为什么 weight_in_grams 是 i32 而不是 u32？
//   u32 存不了负数，"传 -2210 触发 panic"就没法测了。本仓库把这题改成 i32，
//   正是为了能测"负数重量"这个错误场景（官方原版是 u32，改用 0 克来测）。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

#[derive(Debug)]
struct Package {
    sender_country: String,    // 发件国
    recipient_country: String, // 收件国
    weight_in_grams: i32,      // 重量（克）
}

impl Package {
    // 关联函数：没有 self，所以用 Package::new(...) 调用
    fn new(sender_country: String, recipient_country: String, weight_in_grams: i32) -> Package {
        // 重量必须为正，否则直接 panic（第一个测试靠这个 panic 通过）
        if weight_in_grams <= 0 {
            panic!("Can not ship a weightless package.")
        } else {
            // 字段初始化简写；三个参数在这里被移动进结构体
            Package {
                sender_country,
                recipient_country,
                weight_in_grams,
            }
        }
    }

    // 方法：&self 表示"借这个包裹看一眼"，不修改、不消耗
    fn is_international(&self) -> bool {
        // String 之间可直接用 != 比较内容（标准库实现了 PartialEq）
        // 发件国 != 收件国 → 国际件
        self.sender_country != self.recipient_country
    }

    // 方法：读重量，再乘每克单价，返回运费（单位：分）
    fn get_fees(&self, cents_per_gram: i32) -> i32 {
        // 运费 = 重量（克） × 每克单价（分）
        // 1500 * 3 = 4500；1500 * 6 = 9000，与测试期望一致
        self.weight_in_grams * cents_per_gram
    }
}

// ============================================================================
//                              测 试 代 码
// ============================================================================
// 原题自带的 4 个测试，一个字都没改。

#[cfg(test)]
mod tests {
    use super::*;

    // #[should_panic]：这个测试"必须 panic"才算通过（new 收到 -2210 克）
    #[test]
    #[should_panic]
    fn fail_creating_weightless_package() {
        let sender_country = String::from("Spain");
        let recipient_country = String::from("Austria");

        // 重量为负 → new 内部 panic → 测试判定通过
        Package::new(sender_country, recipient_country, -2210);
    }

    #[test]
    fn create_international_package() {
        let sender_country = String::from("Spain");
        let recipient_country = String::from("Russia");

        let package = Package::new(sender_country, recipient_country, 1200);

        // Spain != Russia → 国际件 → 断言成立
        assert!(package.is_international());
    }

    #[test]
    fn create_local_package() {
        let sender_country = String::from("Canada");
        // clone：收件国也要一个独立的 String 所有权
        let recipient_country = sender_country.clone();

        let package = Package::new(sender_country, recipient_country, 1200);

        // Canada == Canada → 国内件 → 取反后成立
        assert!(!package.is_international());
    }

    #[test]
    fn calculate_transport_fees() {
        let sender_country = String::from("Spain");
        let recipient_country = String::from("Spain");

        let cents_per_gram = 3;

        let package = Package::new(sender_country, recipient_country, 1500);

        assert_eq!(package.get_fees(cents_per_gram), 4500);      // 1500 * 3
        assert_eq!(package.get_fees(cents_per_gram * 2), 9000);  // 1500 * 6
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// impl Package { ... }
//   └─ 开启 impl 块：里面的函数都属于 Package 类型
//
// fn new(...) -> Package
//   └─ 没有 self → 关联函数 → 只能写 Package::new(...)
//
// if weight_in_grams <= 0 { panic!(...) } else { ... }
//   └─ 校验：非法输入直接 panic；合法输入走 else 构造实例
//      （if 是表达式，两个分支都返回 ()，所以整条 if 后面不用接值）
//
// fn is_international(&self) -> bool
//   ├─ &self  ：借实例来读，不消耗
//   └─ -> bool：返回 true/false
//
// self.sender_country != self.recipient_country
//   └─ 用 self. 访问字段，用 != 比较 String 内容
//
// fn get_fees(&self, cents_per_gram: i32) -> i32
//   └─ self 之外再接收一个参数；尾表达式 i32 * i32 直接作为返回值
//
// package.is_international()
//   └─ 方法调用：实例 . 方法名(参数)
//      Rust 会自动帮你把 &package 传进 &self，所以调用时不用写 &
//      （关联函数没有 self，就必须写全 Package::new(...)）
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 返回类型写错：fn is_international(&self) -> String
//    → error[E0308]: mismatched types（expected `String`, found `bool`）
//
// 2. 把 != 写成 ==：
//        self.sender_country == self.recipient_country
//    → 逻辑反了，create_international_package 会 FAILED。
//
// 3. 字段名前忘了 self.：
//        sender_country != recipient_country
//    → error[E0425]: cannot find value `sender_country` in this scope
//
// 4. 把关联函数当方法调：package.new(...)
//    → error[E0599]: no method named `new` found for struct `Package`
//    （new 没有 self，只能用 :: 调）
//
// 5. 把 #[should_panic] 删掉：
//    → fail_creating_weightless_package 里发生 panic，普通测试直接 FAILED。
//
// 6. 把 new 里的 panic 改成返回默认值：
//    → 第一个测试不再 panic，带 #[should_panic] 的测试反而 FAILED
//      （"本该 panic 却没有"也算失败）。
//
// 7. panic! 漏了感叹号：panic("...")
//    → error[E0423]: expected function, found macro `panic`
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. 方法写在 `impl 类型名 { ... }` 里，第一个参数是 self / &self / &mut self；
//   2. 只读用 &self，要改用 &mut self，要消耗用 self；
//   3. 没有 self 的是关联函数，用 `类型名::函数名` 调用（如 Package::new）；
//   4. 方法里访问字段必须写 self.字段名；
//   5. #[should_panic] 让"应该 panic"也变成可测试的行为。
//
// 一句话记忆：**impl 里装方法；&self 借来看；没有 self 就是关联函数，用 :: 调。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test structs3.rs -o structs3.exe
//   .\structs3.exe
// 【预期输出】
//   running 4 tests
//   test tests::calculate_transport_fees ... ok
//   test tests::create_international_package ... ok
//   test tests::create_local_package ... ok
//   test tests::fail_creating_weightless_package ... ok
//
//   test result: ok. 4 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
// ============================================================================
