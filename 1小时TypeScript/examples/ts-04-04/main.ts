interface Named { readonly name: string; }
const source = {name: "午餐", amount: 12};
const view: Named = source;
console.log(view.name);
console.log(source.amount);

export {};
