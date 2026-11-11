class Wallet {
  private amount = 12;
  read(): number { return this.amount; }
}
const wallet = new Wallet();
console.log(wallet.amount);

export {};
