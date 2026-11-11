const source: readonly number[] = [12, 8];
const copied = [...source];
copied.push(5);
console.log(source.join(","));
console.log(copied.join(","));

export {};
