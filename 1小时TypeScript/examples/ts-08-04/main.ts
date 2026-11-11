type Expense = {name: string; amount: number; note: string};
type Brief = Pick<Expense, "name" | "amount">;
type Update = Partial<Expense>;
const brief: Brief = {name: "午餐", amount: 12};
const update: Update = {amount: 15};
console.log(brief.name);
console.log(update.amount);

export {};
