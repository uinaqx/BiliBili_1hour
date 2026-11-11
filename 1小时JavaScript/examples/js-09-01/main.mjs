function parseAmount(text) {
  const value = Number(text);
  if (!Number.isFinite(value)) throw new Error("金额格式有误");
  return value;
}
try {
  console.log(parseAmount("abc"));
} catch (error) {
  console.log(error.message);
}
