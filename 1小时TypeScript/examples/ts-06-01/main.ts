function greet(name: string, prefix = "你好"): string {
  return `${prefix}，${name}`;
}
function note(text?: string): string {
  return text ?? "暂无备注";
}
console.log(greet("小林"));
console.log(note());

export {};
