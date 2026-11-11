type Expense = { name: string; amount: number };
function isExpense(v: unknown): v is Expense {
  return typeof v === "object" && v !== null
    && "name" in v && typeof v.name === "string"
    && "amount" in v && typeof v.amount === "number";
}
const data: unknown = JSON.parse('{"name":"午餐","amount":12}');
if (isExpense(data)) {
  console.log(data.name, data.amount);
}

export {};
