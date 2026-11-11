import { parseAmount, readSaved, total } from "./budget.js";
import type { Expense } from "./budget.js";

const form = document.querySelector("#expense-form");
const nameInput = document.querySelector("#name");
const amountInput = document.querySelector("#amount");
const list = document.querySelector("#items");
const totalElement = document.querySelector("#total");
const message = document.querySelector("#message");
if (!(form instanceof HTMLFormElement)
  || !(nameInput instanceof HTMLInputElement)
  || !(amountInput instanceof HTMLInputElement)
  || !(list instanceof HTMLUListElement)
  || !(totalElement instanceof HTMLElement)
  || !(message instanceof HTMLElement)) {
  throw new Error("请通过完整的 index.html 打开本项目");
}

const key = "typescript-course-expenses-v1";
let items: Expense[] = [];
try {
  items = readSaved(localStorage.getItem(key));
} catch (error: unknown) {
  message.textContent = error instanceof Error ? error.message : "读取记录失败";
}
// 使用已收窄的局部参数，让各函数的输入约定保持清晰。
function render(target: HTMLUListElement, summary: HTMLElement): void {
  target.replaceChildren();
  for (const item of items) {
    const row = document.createElement("li");
    const description = document.createElement("span");
    description.textContent = `${item.name}：${item.amount.toFixed(2)} 元`;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "删除";
    button.addEventListener("click", () => {
      items = items.filter(current => current.id !== item.id);
      persist();
      render(target, summary);
    });
    row.append(description, button);
    target.append(row);
  }
  summary.textContent = total(items).toFixed(2);
}
function persist(): void {
  try {
    localStorage.setItem(key, JSON.stringify(items));
  } catch (error: unknown) {
    if (message instanceof HTMLElement) {
      message.textContent = error instanceof Error ? error.message : "保存失败";
    }
  }
}
const inputName = nameInput;
const inputAmount = amountInput;
const outputList = list;
const outputTotal = totalElement;
const outputMessage = message;
form.addEventListener("submit", event => {
  event.preventDefault();
  const name = inputName.value.trim();
  const amount = parseAmount(inputAmount.value);
  if (name === "") {
    outputMessage.textContent = "请输入开销名称";
    return;
  }
  if (amount === null) {
    outputMessage.textContent = "金额请输入大于等于零的有限数字";
    return;
  }
  const id = items.reduce((max, item) => Math.max(max, item.id), 0) + 1;
  if (!Number.isSafeInteger(id)) {
    outputMessage.textContent = "记录编号已达到上限，请先清理记录";
    return;
  }
  items = [...items, { id, name, amount }];
  outputMessage.textContent = "已添加";
  persist();
  render(outputList, outputTotal);
  inputName.value = "";
  inputAmount.value = "";
  inputName.focus();
});
render(list, totalElement);
