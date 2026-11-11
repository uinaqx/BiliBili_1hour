class Wallet {
  balance: number;
  constructor(initial: number) {
    this.balance = initial;
  }
  add(amount: number): void {
    this.balance += amount;
  }
}
const wallet = new Wallet(10);
wallet.add(5);
console.log(wallet.balance);

export {};
