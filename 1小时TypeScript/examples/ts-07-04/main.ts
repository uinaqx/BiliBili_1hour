interface Printable { print(): string; }
class Expense implements Printable {
  constructor(public name: string, public amount: number) {}
  print(): string { return `${this.name}：${this.amount}元`; }
}
const item: Printable = new Expense("午餐", 12);
console.log(item.print());

export {};
