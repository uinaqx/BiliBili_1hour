type Expense = {
  id: number;
  name: string;
  amount: number;
};
const items: Expense[] = [
  { id: 1, name: "午餐", amount: 12 },
  { id: 2, name: "交通", amount: 8 }
];
console.log(items.map(item => item.name).join("、"));

export {};
