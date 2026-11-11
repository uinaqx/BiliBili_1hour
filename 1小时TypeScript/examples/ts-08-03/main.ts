const defaults = {currency: "CNY", limit: 30};
type Settings = typeof defaults;
const personal: Settings = {currency: "USD", limit: 50};
console.log(personal.currency);
console.log(personal.limit);

export {};
