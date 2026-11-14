// 在完整项目目录的终端运行：swift main.swift
// 1 添加  2 查看  3 删除  0 退出
let actions = ["录入开销", "查看列表", "删除记录", "保存文件"]
for (index, action) in actions.enumerated() {
    print("\(index + 1). \(action)")
}
