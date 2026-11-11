type Transform = (value: number) => number;
function apply(value: number, action: Transform): number {
  return action(value);
}
const double: Transform = (value) => value * 2;
console.log(apply(6, double));

export {};
