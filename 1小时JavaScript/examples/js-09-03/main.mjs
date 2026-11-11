console.log("开始");
const task = Promise.resolve(12);
task.then((amount) => {
  console.log(amount);
});
console.log("当前步骤完成");
