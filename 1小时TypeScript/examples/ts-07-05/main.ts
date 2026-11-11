class Expense {
  static currency = "CNY";
  constructor(public amount: number) {}
  static zero(): Expense { return new Expense(0); }
}
const item = Expense.zero();
console.log(Expense.currency);
console.log(item.amount);

export {};
