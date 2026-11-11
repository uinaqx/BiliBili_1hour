const raw: unknown = "12";
const text = raw as string;
const amount = Number(text);
console.log(typeof text);
console.log(typeof amount);
console.log(amount + 8);

export {};
