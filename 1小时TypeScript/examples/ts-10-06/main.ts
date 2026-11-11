type Item = { amount: number };
function sum<T extends Item>(items: readonly T[]): number {
  return items.reduce((n, item) => n + item.amount, 0);
}
const items = [
  { name: "午餐", amount: 12 },
  { name: "交通", amount: 8 }
];
console.log(sum(items));

export {};
