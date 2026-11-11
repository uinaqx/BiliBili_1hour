const expense = {name: "午餐", amount: 12};
const {name, amount} = expense;
console.log(name, amount);
const text = JSON.stringify(expense);
console.log(text);
const restored = JSON.parse(text);
console.log(restored.amount);
