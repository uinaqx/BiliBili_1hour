type Expense = {name: string; amount: number};
function label(item: Expense): string {
  return `${item.name}：${item.amount}元`;
}
console.log(label({name: "午餐", amount: 12}));

export {};
