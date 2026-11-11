const values: number[] = [12];
const found = values.find((value) => value > 20);
const selected: number | null = null;
console.log(found);
console.log(found ?? 0);
console.log(selected ?? 30);

export {};
