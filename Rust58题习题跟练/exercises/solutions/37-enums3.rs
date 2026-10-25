// ============================================================================
// 第 37 题 · enums3 —— match 解构枚举 + &mut self 方法
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 3 章 · 3.4 枚举；第 4 章 · 4.3 match 模式匹配；第 5 章 · 5.1 方法
// 难度：★★★★☆
// 前置知识：enums1、enums2（枚举与携带数据的变体）、structs1、structs2（结构体字段）、
//           4.3 match 基础、5.1 impl / &self 方法
// ============================================================================
//
// 【题目要求】
// 1. 根据测试里的四种用法，补全 enum Message 的四个变体；
// 2. 在 State::process 里写一个 match，按消息类型调用对应的方法，把状态改对；
// 3. 测试代码、结构体字段、已有方法都不能改。
//
// 原题代码（未完成，仅供对照）：
//     enum Message {
//         // TODO: implement the message variant types based on their usage below
//     }
//
//     struct Point { x: u8, y: u8 }
//
//     struct State {
//         color: (u8, u8, u8),
//         position: Point,
//         quit: bool,
//         message: String
//     }
//
//     impl State {
//         fn change_color(&mut self, color: (u8, u8, u8)) { ... }
//         fn quit(&mut self) { ... }
//         fn echo(&mut self, s: String) { self.message = s }
//         fn move_position(&mut self, p: Point) { ... }
//
//         fn process(&mut self, message: Message) {
//             // TODO: match ...
//         }
//     }
//
//     // 测试里这样调用：
//     state.process(Message::ChangeColor(255, 0, 255));
//     state.process(Message::Echo(String::from("hello world")));
//     state.process(Message::Move(Point { x: 10, y: 15 }));
//     state.process(Message::Quit);
//
// 【解题思路】
// 第一步：从“使用处”反推枚举定义
//   - Message::ChangeColor(255, 0, 255)  → 三个数字   → ChangeColor(u8, u8, u8)
//   - Message::Echo(String::from(...))    → 一个 String → Echo(String)
//   - Message::Move(Point { x, y })       → 一个 Point  → Move(Point)
//   - Message::Quit                       → 无数据      → Quit
//   注意：这里 Move 虽然带的是结构体 Point，但变体本身用的是**圆括号**，
//   所以它是“元组式变体”，而不是 `Move { p: Point }` 那种结构体式。
//
// 第二步：在 process 里写 match，把变体里的数据“拆”出来
//   match message {
//       Message::ChangeColor(r, g, b) => self.change_color((r, g, b)),
//       Message::Echo(s)              => self.echo(s),
//       Message::Move(p)              => self.move_position(p),
//       Message::Quit                 => self.quit(),
//   }
//
// 第三步：检查每个方法需要的参数类型
//   change_color 要一个元组 (u8, u8, u8) → 所以传 (r, g, b) 时要再加一层括号；
//   echo 要 String → 直接把解构出来的 s 传进去；
//   move_position 要 Point → 直接把 p 传进去；
//   quit 不要参数 → 直接调用。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● match 是什么？
//   match 是 Rust 的“多分支选择”，类似别的语言的 switch，但强大得多：
//     match 值 {
//         模式1 => 结果1,
//         模式2 => 结果2,
//         ...
//     }
//   特点：
//   1. 必须“穷举”：所有可能的情况都要写到，否则编译报 E0004；
//   2. 每个分支叫“匹配臂（arm）”，用 `=>`（等号+大于号）连接，用逗号分隔；
//   3. match 本身是一个表达式，可以产生值（本题每个分支都返回 ()，所以不返回值）。
//
// ● 模式解构（destructuring）
//   `Message::ChangeColor(r, g, b)` 不只是“判断是不是 ChangeColor”，
//   它还顺手把里面的三个 u8 分别绑定到新变量 r、g、b 上。
//   同理 `Message::Echo(s)` 把里面的 String 绑定到 s。
//   这就像拆快递：先确认盒子上写的是“颜色”，再打开取出三个数字。
//
// ● 元组作参数为什么要双括号？
//   change_color 只接收一个参数，类型是三元组 (u8,u8,u8)。
//   所以写 `self.change_color((r, g, b))`：外层是函数调用，内层是元组。
//   写成 `self.change_color(r, g, b)` 会被当成三个参数，报 E0061。
//
// ● &mut self 是什么？
//   `impl State { fn change_color(&mut self, ...) }` 表示这个方法可以修改
//   调用它的那个 State。&mut 是“可变借用”，借用期间可以读写，但不夺走所有权。
//   因此调用前 state 必须声明成 `let mut state = ...`，否则报 E0596。
//
// ● 为什么 process 也要 &mut self？
//   因为 process 内部要调用 self.change_color(...)、self.echo(...)，
//   这些方法都要求“可变借用 self”。只有 process 自己持有 &mut self，
//   才有资格把可变借用继续借给它们。
//
// ● #[cfg(test)] mod tests：只在测试编译时包含的模块；
//   use super::*; 把外层的类型和函数引入，测试里才能直接用 State、Message。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

enum Message {
    // 三元组变体：R、G、B 三个颜色分量
    ChangeColor(u8, u8, u8),
    // 一元组变体：携带一段文字
    Echo(String),
    // 一元组变体：携带一个坐标点（Point 在下面定义）
    Move(Point),
    // 单元变体：不带数据
    Quit,
}

struct Point {
    x: u8,
    y: u8,
}

struct State {
    color: (u8, u8, u8),
    position: Point,
    quit: bool,
    message: String,
}

impl State {
    // &mut self：允许修改 self.color
    fn change_color(&mut self, color: (u8, u8, u8)) {
        self.color = color;
    }

    // &mut self：允许修改 self.quit
    fn quit(&mut self) {
        self.quit = true;
    }

    // &mut self：允许修改 self.message；s 的所有权被移动进来
    fn echo(&mut self, s: String) {
        self.message = s
    }

    // &mut self：允许修改 self.position
    fn move_position(&mut self, p: Point) {
        self.position = p;
    }

    // message 按值传入：match 会把里面的数据移动/复制出来
    fn process(&mut self, message: Message) {
        match message {
            // 解构三个 u8，绑定到 r、g、b，再打包成元组传给 change_color
            // 注意 (r, g, b) 外面那层括号是函数调用的括号，里面是元组
            Message::ChangeColor(r, g, b) => self.change_color((r, g, b)),

            // 解构出 String，按值移动给 echo
            Message::Echo(s) => self.echo(s),

            // 解构出 Point，按值移动给 move_position
            Message::Move(p) => self.move_position(p),

            // 没有数据可解构，直接调用 quit()
            Message::Quit => self.quit(),
        }
        // 四个分支都返回 ()，所以整个 match 的类型是 ()，不需要分号也合法；
        // 这里 process 的返回类型也是 ()，类型完全对得上。
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_match_message_call() {
        let mut state = State {
            quit: false,
            position: Point { x: 0, y: 0 },
            color: (0, 0, 0),
            message: "hello world".to_string(),
        };
        state.process(Message::ChangeColor(255, 0, 255));
        state.process(Message::Echo(String::from("hello world")));
        state.process(Message::Move(Point { x: 10, y: 15 }));
        state.process(Message::Quit);

        assert_eq!(state.color, (255, 0, 255));
        assert_eq!(state.position.x, 10);
        assert_eq!(state.position.y, 15);
        assert_eq!(state.quit, true);
        assert_eq!(state.message, "hello world");
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）match 的执行过程
//    拿 message 依次和四个模式比对：
//    - 若是 ChangeColor 变体：把三个 u8 复制给 r、g、b（u8 是 Copy 类型，复制很便宜），
//      执行 self.change_color((r, g, b))，state.color 变成 (255, 0, 255)。
//    - 若是 Echo 变体：String 的所有权从 message 移到 s，再移到 self.message；
//      原来 state.message 里的 "hello world" 被替换掉（值相同，所以断言仍然成立）。
//    - 若是 Move 变体：Point 被移动给 p，再赋给 self.position，坐标变成 (10, 15)。
//    - 若是 Quit：self.quit 被设为 true。
// 2）为什么四条消息执行完，message 仍然是 "hello world"？
//    初始就是 "hello world"，Echo 又写入 "hello world"，所以不变。
//    这是测试给出的巧合，不代表 echo 没生效。
// 3）为什么 match 必须写全四个变体？
//    Rust 要求 match 穷举所有可能。少写一个，编译器会报：
//        error[E0004]: non-exhaustive patterns: `Message::Quit` not covered
//    这种设计能在编译期就阻止“漏处理某种消息”的 bug。
//
// 4）message 是按值传进 process 的，为什么还能解构？
//    process 拿到了 message 的所有权，所以完全有权把里面的数据拆出来（移动走）。
//    如果写成 `fn process(&mut self, message: &Message)`，match 时 s、p 都会变成引用，
//    再传给 echo、move_position 就会类型不匹配。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 枚举变体类型和测试里的用法不一致，例如：
//        Move { p: Point }
//    → 测试写的是 `Message::Move(Point { ... })`（圆括号），
//      会报 error[E0599]: no variant named `Move` found（结构体式不能这样调用）
//
// 2. match 漏掉 Quit：
//    → error[E0004]: non-exhaustive patterns: `Message::Quit` not covered
//
// 3. 传元组时忘了加内层括号：
//        self.change_color(r, g, b)
//    → error[E0061]: this method takes 2 arguments but 4 arguments were supplied
//      （1 个是 &mut self，1 个是 color 元组，所以正常是 2 个）
// 4. echo 传了引用：
//        Message::Echo(s) => self.echo(&s),
//    → error[E0308]: mismatched types，expected `String`, found `&String`
// 5. 解构写成了元组模式：
//        Message::ChangeColor((r, g, b)) => ...
//    → error[E0023]: this pattern has 1 field, but the corresponding variant has 3 fields
// 6. 调用 state 的方法前忘了给 state 加 mut（本题测试已写 mut，不要删）：
//    → error[E0596]: cannot borrow `state` as mutable, as it is not declared as mutable
// 7. 用 rustc 直接编译而不加 --test：
//    → error[E0601]: `main` function not found in crate
//    （本题只有测试模块，没有 main）
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. 枚举变体可以携带数据，形状（圆括号/花括号/字段个数）必须和构造处一致；
//   2. match 用来“判断变体 + 解构数据”，并且必须穷举；
//   3. 元组作为函数参数时，调用处需要双括号：`f((a, b, c))`；
//   4. `&mut self` 让方法能修改调用者，链式前提是变量本身声明为 mut；
//   5. 按值传入的 enum 可以在 match 中把数据移动出来，再交给需要所有权的函数。
//
// 一句话记忆：**match 是“拆快递”：先看标签是哪种变体，再把里面的东西按形状取出来。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test enums3.rs -o enums3.exe
//   .\enums3.exe
// 【预期输出】
//   running 1 test
//   test tests::test_match_message_call ... ok
//
//   test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;
// ============================================================================
