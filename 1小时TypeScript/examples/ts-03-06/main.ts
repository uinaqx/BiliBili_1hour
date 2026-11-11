function total(values: number[]): number {
  let sum = 0;
  for (const value of values) sum += value;
  return sum;
}
console.log(total([12, 8]) * 2);

export {};
