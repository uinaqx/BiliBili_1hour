const values = [3, 8, 12];
const result = values
  .filter((value) => value >= 8)
  .map((value) => value + 1);
console.log(result.join(","));
