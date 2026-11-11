const expenses = [12, 8, 5];
const total = expenses.reduce((sum, amount) => {
  return sum + amount;
}, 0);
console.log(total);
