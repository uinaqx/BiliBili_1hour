# keyof 与索引访问类型

已经有Expense类型时，可以让工具从它推导新的类型。keyof Expense得到它的属性名范围，也就是name和amount组成的联合。Expense方括号amount取得amount属性的类型，所以Amount对应number。这里处理的是类型之间的关系，帮助多个位置共用同一份字段说明，减少重复书写。

field只从允许的属性名里选择，这里保存amount。value按Amount要求保存数字十二。显示时得到amount和十二。以后调整Expense里的字段类型，依赖这些关系的代码也会跟着获得新的检查信息。读类型工具时，先把最外层名称还原为它引用的原始类型，再逐步看取了哪些属性或属性值，复杂表达式也能分层理解。

## 本页总结

- keyof 得到属性名称的联合
- Field 允许 name 或 amount
- 索引访问类型取得某属性的类型
- Amount 对应 number

## 预期输出

```text
amount 12
```
