// ============================================================================
// 第 32 题 · structs1 —— 结构体的三种长相：普通、元组、单元
// ----------------------------------------------------------------------------
// 题目类型：test（让三个 #[test] 测试都通过就算过关）
// 课件位置：第 3 章 · 3.3 结构体（普通结构体；元组结构体、单元结构体为扩展）
// 难度：★★☆☆☆
// 前置知识：变量、函数、基本类型、{:?} 调试打印（参考 primitive_types 系列）
// ============================================================================
//
// 【题目要求】
// 补全三个结构体的定义，并在测试里各自创建出实例：
//   1. ColorClassicStruct —— 普通结构体（C 语言风格），字段 red / green / blue；
//   2. ColorTupleStruct   —— 元组结构体，三个字段没有名字，用 .0 .1 .2 访问；
//   3. UnitLikeStruct     —— 单元结构体，一个字段都没有。
// 三个测试分别检查：green = (0, 255, 0)（纯绿色），以及单元结构体的调试输出。
//
// 原题代码（未完成，仅供对照）：
//     struct ColorClassicStruct {
//         // TODO: 字段定义写在这里
//     }
//
//     struct ColorTupleStruct(/* TODO: 类型写在这里 */);
//
//     #[derive(Debug)]
//     struct UnitLikeStruct;
//
//     #[cfg(test)]
//     mod tests {
//         use super::*;
//
//         #[test]
//         fn classic_c_structs() {
//             // let green = ...
//             assert_eq!(green.red, 0);
//             assert_eq!(green.green, 255);
//             assert_eq!(green.blue, 0);
//         }
//
//         #[test]
//         fn tuple_structs() {
//             // let green = ...
//             assert_eq!(green.0, 0);
//             assert_eq!(green.1, 255);
//             assert_eq!(green.2, 0);
//         }
//
//         #[test]
//         fn unit_structs() {
//             // let unit_like_struct = ...
//             let message = format!("{:?}s are fun!", unit_like_struct);
//             assert_eq!(message, "UnitLikeStructs are fun!");
//         }
//     }
//
// 【解题思路】
// 1. 普通结构体：在花括号里逐个写"字段名: 类型"，用逗号分隔。
//    颜色分量范围是 0~255，用 u8（无符号 8 位整数，最大正好 255）最合适。
// 2. 元组结构体：圆括号里只写类型、不写字段名：struct ColorTupleStruct(u8, u8, u8);
//    创建时像调用函数一样 ColorTupleStruct(0, 255, 0)，访问时用 green.0。
// 3. 单元结构体：struct UnitLikeStruct; —— 连括号都没有。
//    创建时直接写结构体名 UnitLikeStruct（注意没有括号），
//    它没有字段，只用来"占个类型"。
// 4. 测试里分别把 green 创建出来即可；断言都是现成的。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 结构体（struct）是什么？
//   结构体是"自己定义的一种复合类型"，把几个相关的值打包在一起。
//   比如"颜色"由红、绿、蓝三个分量组成，就可以定义一个结构体。
//   打个比方：结构体是一张"表格模板"，实例是按模板填好的一张表。
//
// ● 普通结构体（named-field struct）
//       struct ColorClassicStruct {
//           red: u8,
//           green: u8,
//           blue: u8,
//       }
//   读法："定义一个叫 ColorClassicStruct 的类型，它有三个字段，
//         字段名分别是 red/green/blue，类型都是 u8"。
//   注意：
//     - struct 关键字开头，名字用大驼峰（ColorClassicStruct）；
//     - 每个字段写成 `名字: 类型`，字段之间用逗号分隔；
//     - 最后一个字段后面可以留逗号（Rust 允许，推荐留）；
//     - 定义结构体**不分配内存**，它只是"图纸"。
//
// ● 创建实例（实例化）
//       let green = ColorClassicStruct { red: 0, green: 255, blue: 0 };
//   花括号里给每个字段赋值，字段顺序无所谓，但**一个都不能少**。
//   `red: 0` 里的 red 是字段名，0 是值。字段值的类型必须和定义一致。
//
// ● u8 是什么？
//   u8 = unsigned 8-bit integer，无符号 8 位整数，范围 0~255。
//   颜色分量正好是这个范围，所以用 u8 很自然。
//   如果写成 i32 也能编译通过（0/255 都放得下），只是语义上不如 u8 贴切。
//
// ● 元组结构体（tuple struct）
//       struct ColorTupleStruct(u8, u8, u8);
//   它像元组一样"只有位置、没有名字"。适合"字段含义从类型名就能看出来"的场景。
//   创建：let green = ColorTupleStruct(0, 255, 0);
//   访问：green.0、green.1、green.2（下标从 0 开始）。
//
// ● 单元结构体（unit-like struct）
//       struct UnitLikeStruct;
//   没有任何字段，长得像一个"单元类型 ()"，所以叫单元结构体。
//   它有什么用？通常用来表示"某种标记/某种状态"，不需要携带数据。
//   创建：let x = UnitLikeStruct;    // 注意：没有括号，也没有花括号！
//
// ● #[derive(Debug)] 是干什么的？
//   它让编译器自动为这个类型实现 Debug 特征，从而可以用 {:?} 打印。
//     println!("{:?}", x);   → 打印调试格式
//     println!("{}", x);     → 需要 Display 特征，结构体默认没有，会报错
//   本题单元结构体要参与 format!("{:?}s are fun!", ...)，
//   所以必须能 Debug 打印——原题已经帮你写好了 #[derive(Debug)]。
//   普通结构体和元组结构体在本题里只用字段比较，不需要 Debug。
//
// ● 为什么结构体定义写在 mod tests 外面？
//   结构体定义在文件顶层（父模块），测试模块 tests 里用 `use super::*;`
//   把父模块的东西引进来。super 表示"上一层模块"，* 表示"全部"。
//   如果结构体写在 tests 里面，测试外的代码就看不到它了。
//
// ● format! 是什么？
//   format! 和 println! 用法一样，但不打印，而是"把格式化结果变成 String 返回"。
//   所以 message 是一个 String，可以拿去和字符串字面量比较。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

// ① 普通结构体：三个有名字的字段，类型都是 u8
struct ColorClassicStruct {
    red: u8,
    green: u8,
    blue: u8,
}

// ② 元组结构体：只有类型，没有字段名；末尾的分号不能少
struct ColorTupleStruct(u8, u8, u8);

// ③ 单元结构体：一个字段都没有，只有名字和分号
// #[derive(Debug)] 让它可以被 {:?} 打印，输出就是类型名 "UnitLikeStruct"
#[derive(Debug)]
struct UnitLikeStruct;

#[cfg(test)]
mod tests {
    // 把父模块里的结构体引入本模块，这样才能直接用名字
    use super::*;

    #[test]
    fn classic_c_structs() {
        // 实例化普通结构体：给每个字段赋值
        // 0 是红色，255 是绿色，0 是蓝色 → 纯绿色
        let green = ColorClassicStruct {
            red: 0,
            green: 255,
            blue: 0,
        };

        // 用"实例.字段名"读取字段
        assert_eq!(green.red, 0);
        assert_eq!(green.green, 255);
        assert_eq!(green.blue, 0);
    }

    #[test]
    fn tuple_structs() {
        // 实例化元组结构体：像调用函数一样，按顺序给出三个值
        let green = ColorTupleStruct(0, 255, 0);

        // 用"实例.下标"读取字段，下标从 0 开始
        assert_eq!(green.0, 0);
        assert_eq!(green.1, 255);
        assert_eq!(green.2, 0);
    }

    #[test]
    fn unit_structs() {
        // 实例化单元结构体：只写类型名，不加任何括号
        let unit_like_struct = UnitLikeStruct;

        // {:?} 是 Debug 格式化，对单元结构体输出其类型名 "UnitLikeStruct"
        // format! 返回 String，拼成 "UnitLikeStructs are fun!"
        let message = format!("{:?}s are fun!", unit_like_struct);

        assert_eq!(message, "UnitLikeStructs are fun!");
    }
}

// ============================================================================
//                            逐 行 解 析
// ============================================================================
//
// struct ColorClassicStruct { red: u8, green: u8, blue: u8 }
//   ├─ struct        ：定义结构体的关键字
//   ├─ ColorClassicStruct：类型名（大驼峰命名法）
//   └─ { 字段名: 类型, ... }：字段列表
//
// struct ColorTupleStruct(u8, u8, u8);
//   ├─ 圆括号里只有类型，没有名字
//   └─ 末尾的 `;` 必须有（因为它是"声明"，不是带函数体的块）
//
// struct UnitLikeStruct;
//   └─ 只有名字 + 分号，没有任何字段
//
// let green = ColorClassicStruct { red: 0, green: 255, blue: 0 };
//   ├─ 类型名 + { 字段: 值, ... }  = 创建一个实例
//   └─ 字段顺序可以打乱，但字段名必须写全
//
// let green = ColorTupleStruct(0, 255, 0);
//   └─ 括号里按定义顺序给值，第一个就是 .0
//
// green.red  /  green.0
//   └─ 前者按名字访问，后者按位置访问
//
// let unit_like_struct = UnitLikeStruct;
//   └─ 注意：没有 ()，也没有 {}；单元结构体本身就是一个完整的值
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 单元结构体实例化时多写了括号：
//        let unit_like_struct = UnitLikeStruct();
//    → error[E0423]: expected value, found struct `UnitLikeStruct`
//      help: use struct literal syntax instead: `UnitLikeStruct {}`
//    正确的是直接写 UnitLikeStruct。
//
// 2. 普通结构体实例化漏字段：
//        ColorClassicStruct { red: 0, green: 255 }
//    → error[E0063]: missing field `blue` in initializer
//
// 3. 元组结构体定义漏了末尾分号：
//        struct ColorTupleStruct(u8, u8, u8)
//    → error: expected item, found `struct`（下一行被当成字段了）
//
// 4. 元组结构体用字段名访问：
//        green.red
//    → error[E0609]: no field `red` on type `ColorTupleStruct`
//    元组结构体只能用 .0/.1/.2。
//
// 5. 普通结构体字段类型写成 i32 也能过，但 255 更适合 u8；
//    如果写成 u8 却赋值 300：→ error: literal out of range for `u8`
//
// 6. 忘记 #[derive(Debug)] 却用 {:?} 打印：
//    → error[E0277]: `UnitLikeStruct` doesn't implement `Debug`
//
// 7. 用 {} 打印结构体：
//        println!("{}", unit_like_struct)
//    → error[E0277]: `UnitLikeStruct` doesn't implement `Display`
//    （{} 需要 Display，结构体默认只有 Debug）
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. 普通结构体：struct 名字 { 字段: 类型, ... }；
//   2. 元组结构体：struct 名字(类型, 类型, ...);  用 .0/.1 访问；
//   3. 单元结构体：struct 名字;  创建时只写名字，不带括号；
//   4. 实例化普通结构体要写全所有字段，字段顺序随意；
//   5. #[derive(Debug)] + {:?} 是打印结构体内容的标准方式。
//
// 一句话记忆：**结构体有三种长相：有名有姓、只有位置、什么都没有。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test structs1.rs -o structs1.exe
//   .\structs1.exe
// 【预期输出】
//   running 3 tests
//   test tests::classic_c_structs ... ok
//   test tests::tuple_structs ... ok
//   test tests::unit_structs ... ok
//
//   test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
// ============================================================================
