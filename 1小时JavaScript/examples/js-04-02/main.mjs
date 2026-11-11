function label(amount) {
  if (amount < 0) {
    return "金额需为非负数";
  }
  return "已记录";
}
console.log(label(-2));
console.log(label(12));
