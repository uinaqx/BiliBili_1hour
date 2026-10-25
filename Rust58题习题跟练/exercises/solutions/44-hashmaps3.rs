// ============================================================================
// 第 44 题 · hashmaps3 —— 用 HashMap 做一张球队战绩表
// ----------------------------------------------------------------------------
// 题目类型：test（让三个测试全部通过就算过关）
// 课件位置：第 6 章 · 6.1.2 HashMap（entry API、基于旧值更新）；
//           3.3 结构体；3.1 字符串方法（lines、split、parse、to_string）
// 难度：★★★★☆
// 前置知识：hashmaps1、hashmaps2（HashMap、entry + or_insert）、
//           structs1（结构体与字段）、strings3（字符串方法）
// ============================================================================
//
// 【题目要求】
// 输入是一个多行字符串，每行格式：
//     "主队名,客队名,主队进球,客队进球"
// 例如 "England,France,4,2" 表示英格兰进 4 球、法国进 2 球。
// 请为每支球队统计：
//     goals_scored   —— 这支球队自己进了多少球
//     goals_conceded —— 这支球队被对手进了多少球（失球）
// 最后返回 HashMap<String, Team>。
//
// 原题代码（未完成，仅供对照）：
//     for r in results.lines() {
//         let v: Vec<&str> = r.split(',').collect();
//         let team_1_name = v[0].to_string();
//         let team_1_score: u8 = v[2].parse().unwrap();
//         let team_2_name = v[1].to_string();
//         let team_2_score: u8 = v[3].parse().unwrap();
//         // TODO: Populate the scores table ...
//     }
//
// 【解题思路】
// 1. 对每一行，先拿到两个队名和两个进球数（代码已给）。
// 2. 每支球队在表里都应该有一条记录，第一次遇到时初始化为 0：
//        scores.entry(team_1_name)
//              .or_insert(Team { goals_scored: 0, goals_conceded: 0 });
// 3. entry().or_insert() 返回 `&mut Team`，拿到它就能直接改字段：
//        team_1.goals_scored += team_1_score;
//        team_1.goals_conceded += team_2_score;  // 对手进的球就是自己的失球
// 4. 客队同理，只是“进球/失球”要对调：
//        team_2.goals_scored += team_2_score;
//        team_2.goals_conceded += team_1_score;
// 5. 注意：必须先算完 team_1 再用同一个 scores 去 entry team_2，
//    否则会同时存在两个 &mut 借用（借用规则不允许）。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 整体思路：像记账一样“累加”
//   每读一行比赛结果，就给两支球队各记一笔：
//   自己进球 += 本队得分；自己失球 += 对方得分。
//   同一支球队可能出现在多行里（英格兰踢了两场），所以必须“累加”，不能覆盖。
//
// ● `results.lines()` 是什么？
//   String 的 lines() 方法按行切分，返回一个迭代器，每项是一行 &str（不含换行符）。
//   例："a\nb\n".lines() 得到 "a"、"b"。
//   因为 results 是 String，lines() 只是借用它，不会消耗它。
//
// ● `r.split(',').collect::<Vec<&str>>()`
//   split(',') 按逗号切成若干 &str 片段；
//   collect() 把迭代器收集成集合，这里由 `let v: Vec<&str>` 指定成 Vec。
//   对 "England,France,4,2"：
//       v[0] = "England"  v[1] = "France"  v[2] = "4"  v[3] = "2"
//   注意 v 里的 &str 借用的是 results 内部的文本。
//
// ● `.to_string()` 为什么必须调用？
//   因为表是 HashMap<String, Team>，键必须是拥有所有权的 String。
//   v[0] 只是 &str，借用 results；用 to_string() 复制一份独立的 String 才能当键。
//
// ● `.parse().unwrap()` 是什么？
//   parse() 把字符串解析成数字，返回 Result（成功 Ok(数字)，失败 Err(原因)）。
//   目标类型由左边的类型标注 `: u8` 决定，所以这里解析成 u8。
//   unwrap() 表示“如果是 Ok 就取出来，如果是 Err 就直接 panic”。
//   本题输入格式固定，解析一定成功，所以用 unwrap 没问题。
//
// ● `scores.entry(队名)` 与 `or_insert(初始值)`
//   entry 找到这个键的位置；or_insert 在“键不存在”时插入给定的 Team，
//   在“键已存在”时保持原值。它返回 `&mut Team`，指向表里的那条记录。
//   有了这个可变引用，就能直接 `team.goals_scored += 1`。
//
// ● 为什么用 `Team { goals_scored: 0, goals_conceded: 0 }` 初始化？
//   第一次遇到某队时，它还没有任何进球/失球，从 0 开始累加。
//   结构体每个字段都必须写全，不能只写一个。
//
// ● `&mut Team` 上直接改字段
//   `team_1.goals_scored += team_1_score;`
//   等价于 `(*team_1).goals_scored += team_1_score;`，
//   Rust 会自动解引用，字段访问不需要手动写 *。
//
// ● 借用规则提醒（本题的隐藏考点）
//   team_1 是 scores 的可变借用；在它“还活着”（后面还会用）的时候，
//   不能再调用 scores.entry(...) 借第二次。所以我们先完成 team_1 的累加，
//   team_1 最后一次使用后借用结束（NLL，参考 move_semantics5），
//   再借 team_2 就合法了。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

use std::collections::HashMap;

// 一支球队的战绩：进球数、失球数
struct Team {
    goals_scored: u8,
    goals_conceded: u8,
}

fn build_scores_table(results: String) -> HashMap<String, Team> {
    // 队名 → 战绩
    let mut scores: HashMap<String, Team> = HashMap::new();

    // 逐行读取比赛结果
    for r in results.lines() {
        // 按逗号切分，收集成 Vec<&str>
        let v: Vec<&str> = r.split(',').collect();
        // 复制队名：&str → String，才能作为 HashMap 的键
        let team_1_name = v[0].to_string();
        // 解析进球数：类型标注 u8 决定 parse 的目标类型
        let team_1_score: u8 = v[2].parse().unwrap();
        let team_2_name = v[1].to_string();
        let team_2_score: u8 = v[3].parse().unwrap();

        // 主队：不存在就先插入一条 0:0 的记录，拿到 &mut Team
        let team_1 = scores
            .entry(team_1_name)
            .or_insert(Team {
                goals_scored: 0,
                goals_conceded: 0,
            });
        // 主队进球 += 自己的得分
        team_1.goals_scored += team_1_score;
        // 主队失球 += 对手的得分
        team_1.goals_conceded += team_2_score;

        // 主队的借用到这里结束，可以再次可变借用 scores 了
        // 客队：同样先确保表里有记录
        let team_2 = scores
            .entry(team_2_name)
            .or_insert(Team {
                goals_scored: 0,
                goals_conceded: 0,
            });
        // 客队进球 += 客队得分；客队失球 += 主队得分
        team_2.goals_scored += team_2_score;
        team_2.goals_conceded += team_1_score;
    }

    // 返回整张表（所有权交给调用者）
    scores
}

#[cfg(test)]
mod tests {
    use super::*;

    fn get_results() -> String {
        let results = "".to_string()
            + "England,France,4,2\n"
            + "France,Italy,3,1\n"
            + "Poland,Spain,2,0\n"
            + "Germany,England,2,1\n";
        results
    }

    #[test]
    fn build_scores() {
        let scores = build_scores_table(get_results());

        let mut keys: Vec<&String> = scores.keys().collect();
        keys.sort();
        assert_eq!(
            keys,
            vec!["England", "France", "Germany", "Italy", "Poland", "Spain"]
        );
    }

    #[test]
    fn validate_team_score_1() {
        let scores = build_scores_table(get_results());
        let team = scores.get("England").unwrap();
        assert_eq!(team.goals_scored, 5);
        assert_eq!(team.goals_conceded, 4);
    }

    #[test]
    fn validate_team_score_2() {
        let scores = build_scores_table(get_results());
        let team = scores.get("Spain").unwrap();
        assert_eq!(team.goals_scored, 0);
        assert_eq!(team.goals_conceded, 2);
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）把四行比赛手算一遍
//    England,France,4,2 → England 进 4 失 2；France 进 2 失 4
//    France,Italy,3,1   → France 再进 3（共 5）再失 1（共 5）；Italy 进 1 失 3
//    Poland,Spain,2,0   → Poland 进 2 失 0；Spain 进 0 失 2
//    Germany,England,2,1→ Germany 进 2 失 1；England 再进 1（共 5）再失 2（共 4）
//    所以测试里 England 是 5 进球、4 失球；Spain 是 0 进球、2 失球。
//    （France 是 5 进 5 失，但没有测试断言它。）
// 2）为什么同一支球队能正确累加？
//    因为 or_insert 只在第一次遇到时创建 0:0，后续遇到直接返回已有记录的
//    可变引用，`+=` 就是在旧值上继续加。如果用 insert，每次都会覆盖成新的
//    0:0 再加，之前的战绩就丢了。
// 3）为什么先处理 team_1 再处理 team_2？
//    两者都是对 scores 的可变借用。如果写成：
//        let t1 = scores.entry(...).or_insert(...);
//        let t2 = scores.entry(...).or_insert(...);
//        t1.goals_scored += ...;
//    编译器会报 E0499：t1 的借用还活着时就又借了 t2。
//    本题写法在 t2 借用前已经用完 t1，符合 NLL（非词法生命周期）规则。
// 4）测试里的 keys 为什么能跟字符串字面量比较？
//    keys 是 Vec<&String>，右边 vec!["England", ...] 是 Vec<&str>。
//    标准库实现了 String 与 str 的相等比较，所以两个 Vec 可以逐元素比较。
// 5）`scores.get("England")` 为什么不用 String？
//    HashMap::get 的参数是“可以被借成键类型”的引用。
//    String 实现了 Borrow<str>，所以可以用 &str 去查 String 键，
//    避免为了查询临时创建一个 String。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 只统计进球，忘了失球：
//    → validate_team_score_1 失败：England 的 goals_conceded 是 0 而不是 4
// 2. 进球和失球写反：
//        team_1.goals_conceded += team_1_score;
//    → 断言失败（England 失球会变成 5）
// 3. 用 insert 覆盖已有战绩：
//        scores.insert(team_1_name, Team { ... });
//    → 每行都从 0 开始，England 最终只有 1 球，validate_team_score_1 失败
// 4. 同时持有两个可变借用：
//        let t1 = scores.entry(...).or_insert(...);
//        let t2 = scores.entry(...).or_insert(...);
//    → error[E0499]: cannot borrow `scores` as mutable more than once at a time
//
// 5. 结构体初始化漏字段：
//        Team { goals_scored: 0 }
//    → error[E0063]: missing field `goals_conceded` in initializer of `Team`
//
// 6. 忘了 to_string：
//        scores.entry(v[0])
//    → expected `String`, found `&str`
//
// 7. 解析类型写错：
//        let team_1_score = v[2].parse().unwrap();  // 无法推断类型
//    → error[E0282]: type annotations needed
//    必须写 `: u8` 或 `parse::<u8>()`。
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. `entry(键).or_insert(初始值)` 可以“没有就建、有就取”，拿到 &mut V；
//   2. 拿到可变引用后可以直接改结构体字段，实现累加统计；
//   3. 同一 HashMap 同时只能有一个可变借用，算完一队再借另一队；
//   4. `lines()`、`split()`、`parse()`、`to_string()` 是处理文本数据的常用组合；
//   5. parse 的目标类型要靠类型标注或涡轮鱼语法指定；
//   6. 用 &str 查询 String 键是允许的（Borrow 机制）。
//
// 一句话记忆：**entry 负责“开账户”，or_insert 负责“新账户余额为 0”，然后用 += 记账。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test hashmaps3.rs -o hashmaps3.exe
//   .\hashmaps3.exe
// 【预期输出】
//   running 3 tests
//   test tests::build_scores ... ok
//   test tests::validate_team_score_1 ... ok
//   test tests::validate_team_score_2 ... ok
//
//   test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;
// ============================================================================
