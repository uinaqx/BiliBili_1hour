const items = [{name: "午餐", amount: 12}];
const saved = JSON.stringify(items);
const restored = JSON.parse(saved);
console.log(restored[0].name);
console.log(restored[0].amount);
// 网页中：localStorage.setItem("expenses", saved)
// 读取时：localStorage.getItem("expenses")
