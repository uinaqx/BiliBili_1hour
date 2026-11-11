function readAmount(raw) {
  if (raw.trim() === "") return null;
  const amount = Number(raw);
  if (!Number.isFinite(amount) || amount < 0) return null;
  return amount;
}
console.log(readAmount("12"));
console.log(readAmount("abc"));
console.log(readAmount(""));
