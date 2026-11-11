function readAmount(value: unknown): number {
  if (typeof value === "number") {
    return value;
  }
  return 0;
}
console.log(readAmount(12));
console.log(readAmount("12"));

export {};
