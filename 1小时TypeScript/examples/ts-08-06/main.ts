// tsconfig.json 中启用 strict: true
function length(text: string | null): number {
  return text.length;
}
console.log(length(null));

export {};
