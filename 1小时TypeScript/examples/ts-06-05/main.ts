function get<T, K extends keyof T>(item: T, key: K): T[K] {
  return item[key];
}
const expense = {name: "午餐", amount: 12};
console.log(get(expense, "name"));
console.log(get(expense, "amount") + 8);

export {};
