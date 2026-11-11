function label(value: number | string): string {
  if (typeof value === "number") return value.toFixed(0);
  return value.trim();
}
console.log(label(12.6));
console.log(label("  午餐  "));

export {};
