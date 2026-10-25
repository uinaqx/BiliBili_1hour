// ============================================================================
// 第 43 题 · hashmaps2 —— entry + or_insert：只在该键不存在时插入
// ----------------------------------------------------------------------------
// 题目类型：test（让四个测试全部通过就算过关）
// 课件位置：第 6 章 · 6.1.2 HashMap 的 entry API（or_insert）
// 难度：★★★☆☆
// 前置知识：hashmaps1（HashMap 的 new/insert/get）、enums2（枚举变体）、
//           derive 属性（enums1）、4.2 for 循环
// ============================================================================
//
// 【题目要求】
// 篮子里已有 Apple(4)、Mango(2)、Lychee(5)。请遍历 fruit_kinds，
// 把“篮子里还没有的水果”各放 1 个进去；已有水果的数量**一个都不能改**。
// 最终要求：至少 5 种水果、总数超过 11、且没有哪种水果数量为 0。
//
// 原题代码（未完成，仅供对照）：
//     fn fruit_basket(basket: &mut HashMap<Fruit, u32>) {
//         let fruit_kinds = vec![
//             Fruit::Apple, Fruit::Banana, Fruit::Mango, Fruit::Lychee, Fruit::Pineapple,
//         ];
//
//         for fruit in fruit_kinds {
//             // TODO: Insert new fruits if they are not already present in the
//             // basket. Note that you are not allowed to put any type of fruit that's
//             // already present!
//         }
//     }
//
// 【解题思路】
// 1. 题目要求“存在就跳过，不存在才插入”，这正是 HashMap 的 entry API 的用途：
//        basket.entry(fruit).or_insert(1);
// 2. 读法：拿 fruit 去“查询入口” entry；如果这个键是空的（Vacant），
//    就插入默认值 1；如果键已存在（Occupied），就保持原值不动。
// 3. 遍历 fruit_kinds 里有 5 种水果：
//    Apple、Mango、Lychee 已存在 → 保持 4、2、5 不变；
//    Banana、Pineapple 不存在 → 各插入 1。
//    结果：5 种水果，总数 4 + 2 + 5 + 1 + 1 = 13 > 11，且没有 0。
// 4. 注意不能直接用 insert：insert 会覆盖已有数量，把 Apple 从 4 改成 1，
//    第一个测试就会失败。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● HashMap 的“查一次、改一次”问题
//   假设你想实现“不存在才插入”。最直白的写法是：
//        if !basket.contains_key(&fruit) {
//            basket.insert(fruit, 1);
//        }
//   这能工作，但要查两次表（contains_key 一次、insert 一次），
//   而且中间的代码如果更复杂，还容易写出“查完又被别人改了”的逻辑漏洞。
//   为此标准库提供了 entry API：一次查找，直接拿到“这个位置的修改权”。
//
// ● entry 方法
//       let e = basket.entry(fruit);
//   参数是键（这里按值传入 Fruit），返回一个 `Entry` 枚举，它只有两种情况：
//       Entry::Occupied(内部值)  —— 键已存在
//       Entry::Vacant(空位)      —— 键不存在
//   注释：Entry 是标准库内部类型，初学不需要手写它的名字，知道它代表
//   “这个键当前的位置状态”即可。
//
// ● or_insert 方法
//       basket.entry(fruit).or_insert(1)
//   含义：如果空位，就插入 1；如果已有值，就返回已有的值。
//   返回值是 `&mut V`（这里 V = u32），也就是“指向表中那个数量的可变引用”，
//   所以你可以接着 `*... += 1` 修改它（hashmaps3 会用到）。
//   本题只关心“插入”，返回值可以不管（丢弃 &mut 引用不会报错）。
//
// ● 为什么不覆盖已有水果？
//   or_insert 的名字里 or 就是“或者”：有值就用有的，没有才用默认值。
//   而 insert 是“无条件写入”，会把旧值顶掉。
//   题目明确说“不允许再插入已有的水果”，所以必须用 entry/or_insert。
//
// ● 为什么 Fruit 要 derive(Hash, PartialEq, Eq)？
//   HashMap 要当键的类型必须满足两个条件：
//   1. Hash：能算出哈希值，用来决定放在哪个“桶”里；
//   2. Eq：能判断两个键是否完全相等。
//   `#[derive(Hash, PartialEq, Eq)]` 让编译器自动生成这两套实现。
//   少了它们，编译器会报 “the trait bound `Fruit: Hash` is not satisfied”。
//   本题的 Fruit 各变体都不带数据，派生出来的比较就是“看是哪个变体”。
//
// ● `&mut HashMap<Fruit, u32>` 参数是什么意思？
//   函数借用调用者的 map，并且允许修改。测试里传的是 `&mut basket`，
//   函数里插入的水果会真正出现在调用者的 basket 中。
//   如果参数写成 `HashMap<Fruit, u32>`（不带 &mut），函数会拿走整个 map，
//   调用后就无法再检查了——测试也通不过编译。
//
// ● for 循环遍历 Vec
//   `for fruit in fruit_kinds` 会逐个“移动”出 vec 里的元素（Fruit 没有实现 Copy）。
//   每次 fruit 是 Fruit 类型，正好可以按值交给 entry 当键。
//   如果写 `for fruit in &fruit_kinds`，fruit 就是 &Fruit，需要改成 entry(fruit.clone())
//   或者调整写法——本题用按值遍历最简单。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

use std::collections::HashMap;

// 作为 HashMap 的键，必须能哈希、能比较相等
#[derive(Hash, PartialEq, Eq)]
enum Fruit {
    Apple,
    Banana,
    Mango,
    Lychee,
    Pineapple,
}

fn fruit_basket(basket: &mut HashMap<Fruit, u32>) {
    let fruit_kinds = vec![
        Fruit::Apple,
        Fruit::Banana,
        Fruit::Mango,
        Fruit::Lychee,
        Fruit::Pineapple,
    ];

    for fruit in fruit_kinds {
        // entry(fruit)：拿到这个键的“入口”
        // or_insert(1)：键不存在才插入 1；已存在则保持原值
        // 返回值 &mut u32 这里用不到，直接丢弃
        basket.entry(fruit).or_insert(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // Don't modify this function!
    fn get_fruit_basket() -> HashMap<Fruit, u32> {
        let mut basket = HashMap::<Fruit, u32>::new();
        basket.insert(Fruit::Apple, 4);
        basket.insert(Fruit::Mango, 2);
        basket.insert(Fruit::Lychee, 5);

        basket
    }

    #[test]
    fn test_given_fruits_are_not_modified() {
        let mut basket = get_fruit_basket();
        fruit_basket(&mut basket);
        assert_eq!(*basket.get(&Fruit::Apple).unwrap(), 4);
        assert_eq!(*basket.get(&Fruit::Mango).unwrap(), 2);
        assert_eq!(*basket.get(&Fruit::Lychee).unwrap(), 5);
    }

    #[test]
    fn at_least_five_types_of_fruits() {
        let mut basket = get_fruit_basket();
        fruit_basket(&mut basket);
        let count_fruit_kinds = basket.len();
        assert!(count_fruit_kinds >= 5);
    }

    #[test]
    fn greater_than_eleven_fruits() {
        let mut basket = get_fruit_basket();
        fruit_basket(&mut basket);
        let count = basket.values().sum::<u32>();
        assert!(count > 11);
    }

    #[test]
    fn all_fruit_types_in_basket() {
        let mut basket = get_fruit_basket();
        fruit_basket(&mut basket);
        for amount in basket.values() {
            assert_ne!(amount, &0);
        }
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）逐种水果看 or_insert 的效果
//    Apple     已存在(4) → Occupied → 保持 4
//    Banana    不存在     → Vacant   → 插入 1
//    Mango     已存在(2) → Occupied → 保持 2
//    Lychee    已存在(5) → Occupied → 保持 5
//    Pineapple 不存在     → Vacant   → 插入 1
//    最终 5 个键，值的和 = 13。
//
// 2）四个测试分别检查什么？
//    test_given_fruits_are_not_modified：Apple/Mango/Lychee 仍是 4/2/5；
//    at_least_five_types_of_fruits：len() >= 5；
//    greater_than_eleven_fruits：总和 > 11（注意是严格大于）；
//    all_fruit_types_in_basket：每个值都不等于 0。
//
// 3）为什么 or_insert(1) 能保证“没有 0”？
//    因为新插入的水果默认值就是 1；已有水果原本就大于 0。
//    如果写 or_insert(0)，虽然种类数够，但最后一个测试会失败。
//
// 4）如果改用 insert 会怎样？
//        basket.insert(fruit, 1);
//    Apple 从 4 变成 1，Mango 从 2 变成 1，Lychee 从 5 变成 1，
//    第一个测试立刻失败。而且总数变成 5，第二个也失败。
//    这说明 insert 和 entry().or_insert() 的语义完全不同。
//
// 5）entry API 的好处
//    - 只做一次哈希查找，效率高；
//    - “检查是否存在”和“插入”是一个原子操作，不会出现检查完状态又变了的窗口；
//    - 返回 &mut V，方便“存在就修改、不存在就初始化”的写法（hashmaps3）。
//
// 6）`*basket.get(&Fruit::Apple).unwrap()` 里的星号
//    get 返回 Option<&u32>；unwrap 得到 &u32；`*` 解引用得到 u32。
//    assert_eq! 要求两边类型能比较，u32 和字面量 4 可以直接比。
//    这里没有用 entry，是因为 get 只需只读查询。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 用 insert 覆盖：
//        basket.insert(fruit, 1);
//    → test_given_fruits_are_not_modified 失败（Apple 变成 1）
//
// 2. 用 contains_key + insert 也能过，但注意 key 的所有权：
//        if !basket.contains_key(&fruit) { basket.insert(fruit, 1); }
//    能过，但查了两次表，不是本题想练的 entry API。
//
// 3. 漏写 derive 中的 Hash：
//    → error[E0277]: the trait bound `Fruit: Hash` is not satisfied
//
// 4. 漏写 PartialEq/Eq：
//    → error[E0277]: the trait bound `Fruit: Eq` is not satisfied
//
// 5. 没有 import：
//    → error[E0433]: failed to resolve: use of undeclared type `HashMap`
//
// 6. 函数签名漏了 &mut：
//        fn fruit_basket(basket: HashMap<Fruit, u32>)
//    → 测试里 `fruit_basket(&mut basket)` 类型不匹配，
//      而且函数拿走所有权后测试也没法再检查 basket。
//
// 7. 在 for 里写 `basket.entry(&fruit)`：
//    → 键类型变成 &Fruit，与 HashMap<Fruit, u32> 不匹配（expected `Fruit`）
//
// 8. 用 or_insert(0)：
//    → all_fruit_types_in_basket 失败（新水果数量为 0）
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. `entry(键)` 返回“入口”，代表该键当前是已占用还是空位；
//   2. `or_insert(默认值)`：不存在才插入，存在则原样返回；
//   3. 它返回 `&mut V`，可以继续修改值；
//   4. 作为 HashMap 键的类型必须实现 Hash + Eq（常用 derive 自动生成）；
//   5. `&mut HashMap` 参数让函数能修改调用者的表，但不夺走所有权；
//   6. insert 是“无条件覆盖”，entry + or_insert 是“没有才插入”，语义不同。
//
// 一句话记忆：**entry 是门卫，or_insert 是“里面没人就放这位，有人就别动”。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test hashmaps2.rs -o hashmaps2.exe
//   .\hashmaps2.exe
// 【预期输出】
//   running 4 tests
//   test tests::all_fruit_types_in_basket ... ok
//   test tests::at_least_five_types_of_fruits ... ok
//   test tests::greater_than_eleven_fruits ... ok
//   test tests::test_given_fruits_are_not_modified ... ok
//
//   test result: ok. 4 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;
// ============================================================================
