// budget.ts
export type Expense = {amount: number};
export function total(items: Expense[]): number {
  return items.reduce((sum, item) => sum + item.amount, 0);
}
