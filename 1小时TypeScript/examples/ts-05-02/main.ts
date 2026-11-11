function format(value: string | number): string {
  if (typeof value === "number") {
    return value.toFixed(1);
  }
  return value.toUpperCase();
}
console.log(format(12));
console.log(format("tea"));

export {};
