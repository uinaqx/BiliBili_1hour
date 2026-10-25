// ============================================================================
// 第 42 题 · hashmaps1 —— 用 HashMap 建一个水果篮
// ----------------------------------------------------------------------------
// 题目类型：test（让两个测试通过就算过关）
// 课件位置：第 6 章 · 6.1.2 键值对集合 HashMap（new、insert、len、values）
// 难度：★★☆☆☆
// 前置知识：String（strings1）、Vec 基础（vecs1）、函数返回值（functions4）
// ============================================================================
//
// 【题目要求】
// fruit_basket() 要返回一个 HashMap<String, u32>：
//   - 键（String）是水果名；
//   - 值（u32）是这种水果的数量。
// 要求：至少 3 种水果；所有水果数量加起来至少 5 个。
// 题目已经帮你放了 2 根香蕉，你需要补上 map 的创建和其余水果。
//
// 原题代码（未完成，仅供对照）：
//     use std::collections::HashMap;
//
//     fn fruit_basket() -> HashMap<String, u32> {
//         let mut basket = // TODO: declare your hash map here.
//
//         // Two bananas are already given for you :)
//         basket.insert(String::from("banana"), 2);
//
//         // TODO: Put more fruits in your basket here.
//
//         basket
//     }
//
// 【解题思路】
// 1. 看返回值类型：`HashMap<String, u32>`。
//    所以 basket 应该是一个“键是 String、值是 u32”的哈希表。
// 2. 创建空表：`HashMap::new()`。
//    至于 K、V 具体是什么类型，编译器会根据返回值类型自动推断。
// 3. 因为要往里 insert，所以必须写 `let mut basket = ...`。
// 4. 已经有 banana: 2，再加两种以上水果，例如：
//        basket.insert(String::from("apple"), 3);
//        basket.insert(String::from("mango"), 1);
//    这样种类 = 3（≥3），总数 = 2+3+1 = 6（≥5），两个测试都能过。
// 5. 最后一行 `basket` 不加分号，把所有权交还给调用者。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● HashMap 是什么？
//   一种“键 → 值”的集合，类似字典：给一个键，就能快速找到对应的值。
//   生活里的例子：手机通讯录（姓名 → 电话）、超市价签（商品 → 价格）、
//   成绩单（学号 → 分数）。本题是“水果名 → 数量”。
//
// ● 为什么需要 use？
//   `HashMap` 不在 Rust 的“预导入（prelude）”里，必须手动引入：
//       use std::collections::HashMap;
//   含义：从标准库（std）的 collections 模块里，把 HashMap 这个名字拿进来用。
//   暂时可以把它当成“使用某个工具前要先 import 一下”。
//
// ● 常见操作
//   let mut map = HashMap::new();   // 创建空表（必须有 mut 才能插入）
//   map.insert(k, v);               // 插入/覆盖，返回 Option<V>（旧值）
//   map.get(&k);                    // 查询，返回 Option<&V>
//   map.len();                      // 键值对个数（= 有几种键）
//   map.contains_key(&k);           // 是否包含某个键
//   map.remove(&k);                 // 删除，返回 Option<V>
//   map.values();                   // 所有值的迭代器
//   map.keys();                     // 所有键的迭代器
//
// ● insert 的两个细节
//   1. 键会被“移动”进表里：`String::from("banana")` 产生的 String 归 map 所有，
//      所以键类型必须是 String，不能是临时借用。
//   2. 如果键已经存在，insert 会用新值覆盖旧值，并返回旧值（Option<V>）。
//      本题每种水果只插入一次，不用关心返回值。
//
// ● 为什么键要用 String 而不是 &str？
//   函数签名已经规定了 `HashMap<String, u32>`。而且 map 需要长期持有键，
//   如果键是 &str，就得保证被借用的文本活得比 map 还久，容易出问题。
//   String 拥有自己的内存，最省心。
//
// ● 测试里的 `basket.values().sum::<u32>()`
//   values() 得到“所有数量”的迭代器（2、3、1……）；
//   sum() 把它们加起来；`::<u32>` 叫“涡轮鱼语法（turbofish）”，
//   用来明确告诉编译器“按 u32 求和”，因为 sum 可以求很多种类型。
//
// ● 测试函数为什么各调用一次 fruit_basket()？
//   每次调用都会重新创建一个新的 map，互不影响。这是“函数返回所有权”的好处。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

use std::collections::HashMap;

fn fruit_basket() -> HashMap<String, u32> {
    // 创建空 HashMap；K、V 类型由返回类型推断为 String、u32
    // mut：后面要调用 insert 修改它
    let mut basket = HashMap::new();

    // 题目已给：2 根香蕉（这一行保持原样）
    basket.insert(String::from("banana"), 2);

    // 再加两种水果：3 个苹果、1 个芒果
    // 每种水果一个键，值是数量（u32）
    basket.insert(String::from("apple"), 3);
    basket.insert(String::from("mango"), 1);

    // 最后一行不加分号：把 basket 的所有权返回给调用者
    // 现在共 3 种水果，总数 2 + 3 + 1 = 6，满足两个断言
    basket
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn at_least_three_types_of_fruits() {
        let basket = fruit_basket();
        assert!(basket.len() >= 3);
    }

    #[test]
    fn at_least_five_fruits() {
        let basket = fruit_basket();
        assert!(basket.values().sum::<u32>() >= 5);
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）`HashMap::new()` 为什么不用写类型参数？
//    函数返回类型已经写明 `HashMap<String, u32>`，编译器从 `basket` 的返回位置
//    反推出 K = String、V = u32。这叫“类型推断”。
//    如果上下文不够明确，也可以写 `HashMap::<String, u32>::new()` 显式指定。
//
// 2）为什么必须写 mut？
//    Rust 的变量默认不可变。insert 需要修改 map 内部的数据，
//    所以编译器要求 `&mut self`，而调用方必须提供可变变量。
//    漏写 mut 会报 E0596（cannot borrow as mutable）。
//
// 3）insert 的返回值去哪了？
//    它返回 `Option<V>`：如果键原本不存在，返回 None；存在则返回被覆盖的旧值。
//    本题不关心返回值，直接 `basket.insert(...);` 丢弃即可（不会报错）。
//
// 4）为什么水果数量用 u32 而不是 i32？
//    数量不可能为负，u32（无符号 32 位整数）更符合语义；
//    而且测试里 `sum::<u32>()` 要求值的类型是 u32。
//
// 5）HashMap 里的顺序是插入顺序吗？
//    不是。HashMap 为了快速查找会对键做哈希，遍历顺序是不确定的
//    （每次运行甚至可能不同）。所以本题只用 len 和 sum，不依赖顺序。
//
// 6）两个测试分别检查什么？
//    at_least_three_types_of_fruits：len() >= 3，即至少三种水果；
//    at_least_five_fruits：所有数量之和 >= 5。
//    注意这是“且”的关系，两个都要满足。我们放了 3 种、共 6 个，稳过。
//
// 7）如果只放两种水果但每种 100 个，能过吗？
//    不能。第一个测试会失败：len() 只有 2，小于 3。
//    如果放三种但每种 1 个，第二个测试会失败：总和 3 < 5。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 忘写 mut：
//        let basket = HashMap::new();
//    → error[E0596]: cannot borrow `basket` as mutable, as it is not declared as mutable
//
// 2. 只声明不初始化：
//        let mut basket;
//    → error[E0381]: used binding `basket` isn't initialized
//
// 3. 键用了 &str：
//        basket.insert("apple", 3);
//    → error[E0308]: mismatched types，expected `String`, found `&str`
//       help: try `String::from("apple")` 或 `"apple".to_string()`
//
// 4. 值用了 i32：
//        basket.insert(String::from("apple"), 3i32);
//    → expected `u32`, found `i32`
//
// 5. 只加了香蕉：
//    → 第一个测试失败：assertion failed: basket.len() >= 3
//
// 6. 三种水果但总数为 3：
//    → 第二个测试失败：assertion failed: ... >= 5
//
// 7. 最后一行写了 `basket;`（带分号）：
//    → expected `HashMap<String, u32>`, found `()`
//
// 8. 忘了 `use std::collections::HashMap;`：
//    → error[E0433]: failed to resolve: use of undeclared type `HashMap`
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. `use std::collections::HashMap;` 引入哈希表；
//   2. `HashMap::new()` 创建空表，类型可由上下文推断；
//   3. 要插入就必须 `let mut`；
//   4. `insert(键, 值)` 会把键的所有权移进表里，键已存在则覆盖；
//   5. `len()` 是键值对个数，`values()` 遍历所有值；
//   6. `sum::<u32>()` 用涡轮鱼语法指定求和类型。
//
// 一句话记忆：**HashMap 就是“查字典”：给键找到值，插入前记得 mut。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test hashmaps1.rs -o hashmaps1.exe
//   .\hashmaps1.exe
// 【预期输出】
//   running 2 tests
//   test tests::at_least_five_fruits ... ok
//   test tests::at_least_three_types_of_fruits ... ok
//
//   test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;
// ============================================================================
