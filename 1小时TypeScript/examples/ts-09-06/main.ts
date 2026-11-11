type Result = { ok: true; amount: number }
  | { ok: false; message: string };
async function load(): Promise<Result> {
  return { ok: true, amount: 12 };
}
async function main(): Promise<void> {
  const result = await load();
  if (result.ok) console.log(result.amount + 8);
  else console.log(result.message);
}
main();

export {};
