# 安装工具并保存第一个文件

先在电脑上安装Node，确认终端能显示node和npm的版本。新建一个课程练习文件夹，在里面通过npm安装TypeScript。打开配套的第一个例子，把这一行文字和显示语句保存为main点ts。message保存一段文字，冒号后面的string说明它属于字符串类型，引号里面就是准备显示的具体内容。

接着用npx调用tsc，对这个文件做类型检查并生成main点js。画面里的strict打开严格检查，target说明生成代码面向的语言版本。最后通过node运行生成的文件，看到你好，TypeScript。每次修改以后先保存，再检查和运行。配套目录已经保留完整代码与固定版本的配置，你可以直接按目录中的说明开始。

## 本页总结

- 安装 Node.js 后可使用 npm
- 项目中安装 TypeScript 编译器
- main.ts 保存源代码
- 编译后用 node 运行 main.js

## 预期输出

```text
你好，TypeScript！
```
