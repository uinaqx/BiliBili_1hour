type Status = "pending" | "paid";
function label(status: Status): string {
  return status === "paid" ? "已付款" : "待付款";
}
console.log(label("paid"));
console.log(label("pending"));

export {};
