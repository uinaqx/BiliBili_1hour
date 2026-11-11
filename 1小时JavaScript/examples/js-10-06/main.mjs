const items = [{amount: 12}, {amount: 8}, {amount: 5}];
const selected = items.filter((item) => item.amount >= 8);
const total = selected.reduce((sum, item) => sum + item.amount, 0);
const message = total <= 30 ? "预算内" : "超出预算";
console.log(total, message);
