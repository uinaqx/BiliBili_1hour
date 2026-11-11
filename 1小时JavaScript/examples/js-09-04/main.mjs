async function loadAmount() {
  const amount = await Promise.resolve(12);
  return amount + 8;
}
console.log("开始");
const total = await loadAmount();
console.log(total);
