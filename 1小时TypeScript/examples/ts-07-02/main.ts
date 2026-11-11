class Wallet {
  private amount = 0;
  add(value: number): void { this.amount += value; }
  get balance(): number { return this.amount; }
}
const wallet = new Wallet();
wallet.add(12);
console.log(wallet.balance);

export {};
