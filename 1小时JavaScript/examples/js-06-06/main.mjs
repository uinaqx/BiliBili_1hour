const a = {amount: 12};
const b = a;
const c = {...a};
b.amount = 30;
console.log(a.amount);
console.log(c.amount);
