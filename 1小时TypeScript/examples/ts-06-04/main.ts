function size<T extends {length: number}>(value: T): number {
  return value.length;
}
console.log(size("hello"));
console.log(size([12, 8, 5]));

export {};
