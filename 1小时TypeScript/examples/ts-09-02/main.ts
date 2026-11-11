function pay(amount: number): void {
  if (amount < 0) throw new Error("金额应大于等于零");
  console.log("支付", amount);
}
try {
  pay(-1);
} catch (error: unknown) {
  if (error instanceof Error) {
    console.log(error.message);
  }
}

export {};
