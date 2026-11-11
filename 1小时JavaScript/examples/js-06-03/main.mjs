const first = {amount: 12};
const second = first;
second.amount = 20;
console.log(first.amount);
console.log(first === second);
