import {readAmount, summary} from "./budget.js";
const key = "javascript-course-expenses-v1";
const message = document.querySelector("#message");
let items = [];
try {
  const saved = JSON.parse(localStorage.getItem(key) ?? "[]");
  if (!Array.isArray(saved) || !saved.every(item => item && typeof item.id === "string" && typeof item.name === "string" && Number.isFinite(item.amount) && item.amount >= 0)) {
    throw new Error("保存的数据格式有误，请点击清空记录重新开始");
  }
  items = saved;
} catch (error) {
  message.textContent = error.message;
}
function save() {
  try { localStorage.setItem(key, JSON.stringify(items)); }
  catch { message.textContent = "本次记录仍可使用，浏览器未能保存，请检查本地存储设置"; }
}
function render() {
  const list = document.querySelector("#list");
  list.replaceChildren();
  for (const item of items) {
    const li = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = `${item.name}：${item.amount}元`;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "删除";
    button.addEventListener("click", () => {
      items = items.filter(record => record.id !== item.id);
      save(); render();
    });
    li.append(label, button); list.append(li);
  }
  const {total, left, within} = summary(items, 30);
  document.querySelector("#summary").textContent = `总额：${total}元；余额：${left}元；${within ? "预算内" : "超出预算"}`;
}
document.querySelector("#form").addEventListener("submit", event => {
  event.preventDefault();
  const name = document.querySelector("#name").value.trim();
  const amount = readAmount(document.querySelector("#amount").value);
  if (name === "" || amount === null) {
    message.textContent = "请填写名称和非负数字金额"; return;
  }
  items.push({id: crypto.randomUUID(), name, amount});
  message.textContent = "已记录";
  save(); render(); document.querySelector("#form").reset();
});
document.querySelector("#reset").addEventListener("click", () => {
  items = []; message.textContent = "已清空"; save(); render();
});
render();
