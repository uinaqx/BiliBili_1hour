# TypeScript 课程配套示例

每页对应一个文件夹。`main.ts` 是原始示例；预期报错题目同时提供 `fixed.ts` 和 `expected-error.txt`；`out` 保存本次真实编译结果。

## 快速开始

先在课程工程根目录执行 `npm ci`。例如：

```powershell
node node_modules/typescript/lib/tsc.js --strict --target ES2022 --module commonjs examples/ts-01-02/main.ts
node examples/ts-01-02/main.js
```

网页示例 `ts-09-05` 请通过本地 HTTP 服务打开；完整项目见 [完整项目/README.md](完整项目/README.md)。

| 时间 | 主题 | 代码 |
|---|---|---|
| 00:00:00 | 从一个有类型的程序开始 | [ts-01-01/main.ts](ts-01-01/main.ts) |
| 00:00:58 | 安装工具并保存第一个文件 | [ts-01-02/main.ts](ts-01-02/main.ts) |
| 00:01:54 | 类型说明与生成后的代码 | [ts-01-03/main.ts](ts-01-03/main.ts) |
| 00:02:52 | let、const 与类型推断 | [ts-01-04/main.ts](ts-01-04/main.ts) |
| 00:03:51 | 读懂第一条类型错误 | [ts-01-05/main.ts](ts-01-05/main.ts) |
| 00:04:52 | 基础类型与显示结果 | [ts-01-06/main.ts](ts-01-06/main.ts) |
| 00:05:50 | 数组类型与元素读取 | [ts-02-01/main.ts](ts-02-01/main.ts) |
| 00:06:50 | 只读数组表达读取用途 | [ts-02-02/main.ts](ts-02-02/main.ts) |
| 00:07:46 | 元组给不同位置安排类型 | [ts-02-03/main.ts](ts-02-03/main.ts) |
| 00:08:42 | 用联合类型描述两种可能 | [ts-02-04/main.ts](ts-02-04/main.ts) |
| 00:09:37 | undefined、null 与默认值 | [ts-02-05/main.ts](ts-02-05/main.ts) |
| 00:10:32 | 练习：元组与数组元素 | [ts-02-06/main.ts](ts-02-06/main.ts) |
| 00:11:31 | 先整理类型，再完成运算 | [ts-03-01/main.ts](ts-03-01/main.ts) |
| 00:12:28 | 用 if 选择处理路线 | [ts-03-02/main.ts](ts-03-02/main.ts) |
| 00:13:23 | 循环处理一组开销 | [ts-03-03/main.ts](ts-03-03/main.ts) |
| 00:14:22 | 参数类型与返回类型 | [ts-03-04/main.ts](ts-03-04/main.ts) |
| 00:15:21 | 箭头函数与数组回调 | [ts-03-05/main.ts](ts-03-05/main.ts) |
| 00:16:21 | 练习：一次调用完成几步计算 | [ts-03-06/main.ts](ts-03-06/main.ts) |
| 00:17:24 | 把一条记录写成对象类型 | [ts-04-01/main.ts](ts-04-01/main.ts) |
| 00:18:21 | type 为数据形状起名字 | [ts-04-02/main.ts](ts-04-02/main.ts) |
| 00:19:19 | interface 与可选属性 | [ts-04-03/main.ts](ts-04-03/main.ts) |
| 00:20:18 | readonly 与结构匹配 | [ts-04-04/main.ts](ts-04-04/main.ts) |
| 00:21:15 | 对象数组与条件筛选 | [ts-04-05/main.ts](ts-04-05/main.ts) |
| 00:22:17 | 练习：补齐必需属性 | [ts-04-06/main.ts](ts-04-06/main.ts) |
| 00:23:17 | 字面量类型列出允许的值 | [ts-05-01/main.ts](ts-05-01/main.ts) |
| 00:24:15 | typeof 把联合类型分成两条路线 | [ts-05-02/main.ts](ts-05-02/main.ts) |
| 00:25:11 | 可选链与空值处理 | [ts-05-03/main.ts](ts-05-03/main.ts) |
| 00:26:09 | 用标签区分不同形状 | [ts-05-04/main.ts](ts-05-04/main.ts) |
| 00:27:02 | 类型断言与真正的数据转换 | [ts-05-05/main.ts](ts-05-05/main.ts) |
| 00:28:01 | 练习：根据类型选择格式 | [ts-05-06/main.ts](ts-05-06/main.ts) |
| 00:29:02 | 默认参数与可选参数 | [ts-06-01/main.ts](ts-06-01/main.ts) |
| 00:29:58 | 用函数类型描述回调 | [ts-06-02/main.ts](ts-06-02/main.ts) |
| 00:30:52 | 泛型保留输入与输出的联系 | [ts-06-03/main.ts](ts-06-03/main.ts) |
| 00:31:46 | 给泛型添加需要的能力 | [ts-06-04/main.ts](ts-06-04/main.ts) |
| 00:32:39 | keyof 约束可以读取的属性名 | [ts-06-05/main.ts](ts-06-05/main.ts) |
| 00:33:39 | 练习：保持容器中的元素类型 | [ts-06-06/main.ts](ts-06-06/main.ts) |
| 00:34:39 | 把数据与方法组织成类 | [ts-07-01/main.ts](ts-07-01/main.ts) |
| 00:35:38 | 访问范围与读取入口 | [ts-07-02/main.ts](ts-07-02/main.ts) |
| 00:36:43 | 继承与 override | [ts-07-03/main.ts](ts-07-03/main.ts) |
| 00:37:41 | implements 核对一组共同能力 | [ts-07-04/main.ts](ts-07-04/main.ts) |
| 00:38:42 | 静态成员与类本身的工具 | [ts-07-05/main.ts](ts-07-05/main.ts) |
| 00:39:41 | 练习：通过公开方法读取 | [ts-07-06/main.ts](ts-07-06/main.ts) |
| 00:40:41 | 枚举为一组状态命名 | [ts-08-01/main.ts](ts-08-01/main.ts) |
| 00:41:41 | keyof 与索引访问类型 | [ts-08-02/main.ts](ts-08-02/main.ts) |
| 00:42:37 | typeof 从已有值取得类型 | [ts-08-03/main.ts](ts-08-03/main.ts) |
| 00:43:31 | Pick 与 Partial 复用已有结构 | [ts-08-04/main.ts](ts-08-04/main.ts) |
| 00:44:34 | 导出类型与导出函数 | [ts-08-05/main.ts](ts-08-05/main.ts) |
| 00:45:32 | 练习：在严格检查下处理空值 | [ts-08-06/main.ts](ts-08-06/main.ts) |
| 00:46:35 | 等待稍后完成的结果 | [ts-09-01/main.ts](ts-09-01/main.ts) |
| 00:47:30 | 用异常传递失败原因 | [ts-09-02/main.ts](ts-09-02/main.ts) |
| 00:48:26 | 先检查未知数据 | [ts-09-03/main.ts](ts-09-03/main.ts) |
| 00:49:21 | 验证 JSON 中的对象 | [ts-09-04/main.ts](ts-09-04/main.ts) |
| 00:50:19 | 检查网页输入元素 | [ts-09-05/main.ts](ts-09-05/main.ts) |
| 00:51:17 | 练习：处理异步查询 | [ts-09-06/main.ts](ts-09-06/main.ts) |
| 00:52:18 | 用类型设计开销记录 | [ts-10-01/main.ts](ts-10-01/main.ts) |
| 00:53:16 | 把统计写成独立函数 | [ts-10-02/main.ts](ts-10-02/main.ts) |
| 00:54:10 | 通过函数集中更新记录 | [ts-10-03/main.ts](ts-10-03/main.ts) |
| 00:55:08 | 让外部输入经过检查 | [ts-10-04/main.ts](ts-10-04/main.ts) |
| 00:56:01 | 检查完整网页项目 | [ts-10-05/main.ts](ts-10-05/main.ts) |
| 00:56:56 | 综合练习与下一步 | [ts-10-06/main.ts](ts-10-06/main.ts) |
