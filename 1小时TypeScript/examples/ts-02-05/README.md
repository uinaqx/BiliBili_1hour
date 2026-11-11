# undefined、null 与默认值

这一组金额里只有十二，find寻找大于二十的元素，结果没有找到，返回undefined。严格检查会把查找结果的类型保留为数字或undefined，提醒后面同时考虑两种情况。selected被主动设为null，表示当前还没有选中金额。它们都能表达暂时缺少值的状态，常见来源各有自己的位置。

直接显示found，会看到undefined。两个问号连接默认值，遇到null或undefined时采用右边的零。selected也因此采用三十。已有的零、空文字或false会按它们原来的值保留。读这种表达式时，先检查左边是否属于空值，再决定使用哪一边，后面的显示和计算就有了清楚的输入。

## 本页总结

- find 没找到时返回 undefined
- null 可主动表达当前为空
- ?? 为 null 或 undefined 提供默认值
- 默认值让后续处理有明确起点

## 预期输出

```text
undefined
0
30
```
