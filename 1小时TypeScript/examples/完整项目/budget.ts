export type Expense = { id: number; name: string; amount: number };
export function total(items: readonly Expense[]): number {
  return items.reduce((sum, item) => sum + item.amount, 0);
}
export function parseAmount(text: string): number | null {
  if (text.trim() === "") return null;
  const value = Number(text);
  return Number.isFinite(value) && value >= 0 ? value : null;
}
export function isExpense(value: unknown): value is Expense {
  return typeof value === "object" && value !== null
    && "id" in value && typeof value.id === "number"
    && Number.isSafeInteger(value.id) && value.id > 0
    && "name" in value && typeof value.name === "string"
    && value.name.trim().length > 0
    && "amount" in value && typeof value.amount === "number"
    && Number.isFinite(value.amount) && value.amount >= 0;
}
export function readSaved(text: string | null): Expense[] {
  if (text === null) return [];
  const value: unknown = JSON.parse(text);
  if (!Array.isArray(value) || !value.every(isExpense)) {
    throw new Error("已保存的记录格式有误，已开启空白列表");
  }
  const ids = new Set(value.map(item => item.id));
  if (ids.size !== value.length) throw new Error("记录编号重复，已开启空白列表");
  return value;
}
