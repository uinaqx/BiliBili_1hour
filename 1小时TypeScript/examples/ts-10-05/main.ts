type Expense = { id: number; name: string; amount: number };
const items: Expense[] = [
  { id: 1, name: "午餐", amount: 12 },
  { id: 2, name: "交通", amount: 8 }
];
const saved = JSON.stringify(items);
const restored: unknown = JSON.parse(saved);
console.log(Array.isArray(restored));
console.log(items.reduce((sum, item) => sum + item.amount, 0));

export {};
