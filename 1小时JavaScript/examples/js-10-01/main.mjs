const expenses = [
  {id: 1, name: "午餐", amount: 12},
  {id: 2, name: "交通", amount: 8}
];
const total = expenses.reduce((sum, item) => sum + item.amount, 0);
console.log(total);
console.log(expenses.map((item) => item.name).join(","));
