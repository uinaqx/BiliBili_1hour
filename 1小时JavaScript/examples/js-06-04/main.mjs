const first = {amount: 12, name: "午餐"};
const second = {...first};
second.amount = 20;
console.log(first.amount);
console.log(second.amount);
console.log(first === second);
