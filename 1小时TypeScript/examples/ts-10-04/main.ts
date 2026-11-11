function parseAmount(text: string): number | null {
  if (text.trim() === "") return null;
  const amount = Number(text);
  return Number.isFinite(amount) && amount >= 0
    ? amount : null;
}
console.log(parseAmount("12.5"));
console.log(parseAmount("abc"));
console.log(parseAmount(""));

export {};
