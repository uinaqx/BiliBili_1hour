type Expense = {name: string; amount: number};
const items: Expense[] = [
  {name: "午餐", amount: 12},
  {name: "交通", amount: 8}
];
const selected = items.filter((item) => item.amount >= 10);
console.log(selected.map((item) => item.name).join(","));

export {};
