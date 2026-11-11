interface Expense {
  name: string;
  amount: number;
  note?: string;
}
const item: Expense = {name: "午餐", amount: 12};
console.log(item.note ?? "暂无备注");

export {};
