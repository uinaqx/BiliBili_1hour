type Expense = {name: string; amount: number};
type Field = keyof Expense;
type Amount = Expense["amount"];
const field: Field = "amount";
const value: Amount = 12;
console.log(field, value);

export {};
