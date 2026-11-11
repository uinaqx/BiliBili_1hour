# TypeScript 开销记录

1. 在本课程工程根目录执行 `npm ci`。
2. 执行 `node node_modules/typescript/lib/tsc.js -p examples/完整项目/tsconfig.json`。
3. 执行 `python -m http.server 8000 --directory examples/完整项目`。
4. 浏览器访问 http://localhost:8000 。

独立使用这个文件夹时，先运行 `npm install --save-dev typescript@5.9.3`，再执行 `npx tsc -p tsconfig.json`、`python -m http.server 8000`。

`budget.ts` 保存类型、统计和数据检查函数；`app.ts` 连接网页操作；`index.html` 提供页面。`dist` 是实际编译生成的浏览器 JavaScript，可由上述命令重新生成。

练习：添加记录、删除记录、刷新后恢复、空名称提示、负数提示、金额零，以及损坏存储数据时的处理。
