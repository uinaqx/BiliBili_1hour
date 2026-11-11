function summary(items, budget) {
  const total = items.reduce((sum, item) => sum + item.amount, 0);
  const left = budget - total;
  return {total, left, within: left >= 0};
}
const result = summary([{amount: 12}, {amount: 8}], 30);
console.log(JSON.stringify(result));
