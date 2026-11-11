const items = [];
function addExpense(name, amount) {
  items.push({name, amount});
}
addExpense("午餐", 12);
addExpense("交通", 8);
console.log(items.length);
console.log(items.reduce((sum, item) => sum + item.amount, 0));
