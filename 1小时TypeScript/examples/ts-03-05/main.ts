const double = (value: number): number => value * 2;
console.log(double(6));
const prices = [10, 20];
const result = prices.map((price) => price + 1);
console.log(result.join(","));

export {};
