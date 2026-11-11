function addTax(price, rate = 0.1) {
  return price * (1 + rate);
}
console.log(addTax(100));
console.log(addTax(100, 0.2));
