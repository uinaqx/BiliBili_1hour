type Expense = { name: string; amount: number };
function total(items: readonly Expense[]): number {
  return items.reduce((sum, item) => sum + item.amount, 0);
}
const items: Expense[] = [
  { name: "午餐", amount: 12 },
  { name: "交通", amount: 8 }
];
console.log(total(items));
console.log(total([]));

export {};
