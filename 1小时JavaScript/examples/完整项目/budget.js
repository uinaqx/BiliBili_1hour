export function readAmount(raw) {
  if (raw.trim() === "") return null;
  const amount = Number(raw);
  return Number.isFinite(amount) && amount >= 0 ? amount : null;
}
export function summary(items, budget) {
  const total = items.reduce((sum, item) => sum + item.amount, 0);
  return {total, left: budget - total, within: total <= budget};
}
