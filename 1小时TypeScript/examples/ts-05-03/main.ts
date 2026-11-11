type User = {name: string; note?: string};
function noteLength(user: User | null): number {
  return user?.note?.length ?? 0;
}
console.log(noteLength({name: "小林", note: "午餐"}));
console.log(noteLength({name: "小林"}));
console.log(noteLength(null));

export {};
