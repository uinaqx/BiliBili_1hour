function identity<T>(value: T): T {
  return value;
}
const amount = identity(12);
const name = identity("午餐");
console.log(amount + 8);
console.log(name.toUpperCase());

export {};
