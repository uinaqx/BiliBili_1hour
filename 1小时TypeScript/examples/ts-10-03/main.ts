type Expense = { id: number; amount: number };
let items: Expense[] = [];
function add(item: Expense): void {
  items = [...items, item];
}
function remove(id: number): void {
  items = items.filter(item => item.id !== id);
}
add({ id: 1, amount: 12 });
add({ id: 2, amount: 8 });
remove(1);
console.log(items.map(item => item.amount).join(","));

export {};
