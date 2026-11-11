import {total} from "./budget.js";
import type {Expense} from "./budget.js";
const items: Expense[] = [{amount: 12}, {amount: 8}];
console.log(total(items));

export {};
