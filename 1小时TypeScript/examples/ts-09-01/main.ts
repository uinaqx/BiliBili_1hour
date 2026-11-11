async function loadAmount(): Promise<number> {
  return 20;
}
async function main(): Promise<void> {
  const amount = await loadAmount();
  console.log(amount);
}
main();

export {};
