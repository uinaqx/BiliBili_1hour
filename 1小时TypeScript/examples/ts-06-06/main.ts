function wrap<T>(value: T): {value: T} {
  return {value};
}
const box = wrap(12);
console.log(box.value + 8);

export {};
