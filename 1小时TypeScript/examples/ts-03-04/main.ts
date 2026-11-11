function remaining(budget: number, spent: number): number {
  return budget - spent;
}
const left = remaining(30, 25);
console.log(left);

export {};
