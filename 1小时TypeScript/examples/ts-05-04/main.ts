type Result =
  | {ok: true; amount: number}
  | {ok: false; message: string};
function show(result: Result): string {
  if (result.ok) return `${result.amount}元`;
  return result.message;
}
console.log(show({ok: true, amount: 12}));
console.log(show({ok: false, message: "请重新输入"}));

export {};
